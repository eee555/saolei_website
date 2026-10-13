import { getDataDomain } from '@putianyi888/vue3-plots';
import { describe, expect, it } from 'vitest';

import { counterVariables, defaultCounterConfig, prepareCounters } from './counter';
import type { CounterEvent, CounterValues, PreparedCounter } from './counter';
import { addTimelineTrack, clampTimeWindow, defaultTimelineConfig, panTimeWindow, timeAtPixel, timelinePalette, timelinePoints, timelineYDomain, zoomTimeWindow } from './timeline';

function counter(values: number[], times = values.map((_value, index) => index * 100)): PreparedCounter {
    return { samples: values.map((value, index) => ({ timeMs: times[index], eventIndex: index, value })), formatter: String, error: '' };
}

describe('timeline slots and colors', () => {
    it('starts with Bvs and Ces in Plot 1, Mov in Plot 2, and independent tracks and settings', () => {
        const first = defaultTimelineConfig();
        const expectedSlots = [[{ key: 'Bvs', color: timelinePalette[0] }, { key: 'Ces', color: timelinePalette[1] }], [{ key: 'Mov', color: timelinePalette[0] }]];
        expect(first.slots).toEqual(expectedSlots);
        expect(first.slotSettings.map((slot) => slot.name)).toEqual(['Plot 1', 'Plot 2']);
        addTimelineTrack(first, 0, 'bvs');
        first.slots[0][0].color = '#fff';
        first.slotSettings[0].height = 300;
        expect(first.slots[1]).toEqual(expectedSlots[1]);
        expect(defaultTimelineConfig()).toEqual({ slots: expectedSlots, slotSettings: [{ name: 'Plot 1', height: 160 }, { name: 'Plot 2', height: 160 }] });
    });

    it('allows duplicate and invalid keys, assigns least-used colors, and retains existing colors', () => {
        const config = defaultTimelineConfig();
        config.slots = [[], []];
        for (let index = 0; index < 11; index++) addTimelineTrack(config, 0, index === 0 ? 'missing' : 'bvs');
        expect(config.slots[0].map((track) => track.color)).toEqual([...timelinePalette, timelinePalette[0]]);
        expect(config.slots[0].filter((track) => track.key === 'bvs')).toHaveLength(10);
        const remaining = config.slots[0].filter((_track, index) => index !== 3);
        config.slots[0].splice(3, 1);
        addTimelineTrack(config, 0, 'bvs');
        expect(config.slots[0].slice(0, -1)).toEqual(remaining);
        expect(config.slots[0].at(-1)?.color).toBe(timelinePalette[3]);
        addTimelineTrack(config, 1, 'bvs');
        expect(config.slots[1]).toEqual([{ key: 'bvs', color: timelinePalette[0] }]);
    });
});

describe('shared timeline time window', () => {
    it('cannot pan a full replay and clamps zoomed panning without changing window length', () => {
        expect(panTimeWindow({ startMs: 0, endMs: 1000 }, 200, 1000)).toEqual({ startMs: 0, endMs: 1000 });
        expect(panTimeWindow({ startMs: 200, endMs: 600 }, -500, 1000)).toEqual({ startMs: 0, endMs: 400 });
        expect(panTimeWindow({ startMs: 200, endMs: 600 }, 900, 1000)).toEqual({ startMs: 600, endMs: 1000 });
        expect(clampTimeWindow({ startMs: -50, endMs: 2050 }, 1000)).toEqual({ startMs: 0, endMs: 1000 });
        expect(clampTimeWindow({ startMs: 0, endMs: 1000 }, 0)).toEqual({ startMs: 0, endMs: 0 });
    });

    it('zooms around the pointer and bounds the window to one millisecond or the whole replay', () => {
        expect(zoomTimeWindow({ startMs: 0, endMs: 1000 }, 0.5, 0.75, 1000)).toEqual({ startMs: 375, endMs: 875 });
        const minimum = zoomTimeWindow({ startMs: 200, endMs: 600 }, 0, 0.5, 1000);
        expect(minimum).toEqual({ startMs: 399.5, endMs: 400.5 });
        expect(zoomTimeWindow(minimum, 100000, 0, 1000)).toEqual({ startMs: 0, endMs: 1000 });
        expect(zoomTimeWindow({ startMs: 0, endMs: 0 }, 0.5, 0.5, 0)).toEqual({ startMs: 0, endMs: 0 });
    });

    it('uses the plotting scale and padding for seeking and clamps outside plot coordinates', () => {
        const window = { startMs: 200, endMs: 600 };
        expect(timeAtPixel(window, 152, 52, 400)).toBe(300);
        expect(timeAtPixel(window, 0, 52, 400)).toBe(200);
        expect(timeAtPixel(window, 1000, 52, 400)).toBe(600);
        expect(Number.isFinite(timeAtPixel(window, 52, 52, 0))).toBe(true);
    });
});

describe('counter-backed timeline data', () => {
    it('prepares one shared result per counter key, including expression errors', () => {
        const config = defaultCounterConfig();
        config.rows = [{ ...config.rows[0], key: 'bvs', expression: 'left', samplingMode: 'button' }];
        config.rows.push({ ...config.rows[0], key: 'broken', expression: 'not_a_variable' });
        const events: CounterEvent[] = [0, 1].map((index) => ({ timeMs: index * 100, eventIndex: index, button: true, boardChanged: true, values: Object.fromEntries(counterVariables.map((key) => [key, index * 4])) as CounterValues }));
        const prepared = prepareCounters(config.rows, events);
        expect(prepared.get('bvs')?.samples.map((sample) => sample.value)).toEqual([0, 4]);
        expect(prepared.get('broken')?.error).toContain('Unknown variable');
        expect(prepared.size).toBe(2);
    });

    it('extends nearest endpoint values to replay boundaries without mutating samples or filtering NaN/Infinity', () => {
        const prepared = counter([2, 6], [100, 500]);
        expect(timelinePoints(prepared, 1000)).toEqual([{ x: 0, y: 2 }, { x: 100, y: 2 }, { x: 500, y: 6 }, { x: 1000, y: 6 }]);
        expect(prepared.samples).toHaveLength(2);
        expect(timelinePoints(counter([NaN, Infinity, -Infinity]), 200).map((point) => point.y)).toEqual([NaN, Infinity, -Infinity]);
        expect(timelinePoints({ ...prepared, error: 'Invalid expression' }, 1000)).toEqual([]);
        expect(timelinePoints(counter([]), 1000)).toEqual([]);
        expect(timelinePoints(counter([1, 2], [-100, 100]), 200)[0]).toEqual({ x: -100, y: 1 });
    });

    it('delegates full-replay shared y domains and non-finite values to vue3-plots, ignoring missing keys', () => {
        const counters = new Map([['small', counter([1, 3])], ['large', counter([200, NaN, Infinity, 900])]]);
        const tracks = ['small', 'missing', 'large', 'small'].map((key) => ({ key, color: '#fff' }));
        const expected = getDataDomain(tracks.flatMap((track) => counters.get(track.key)?.samples.map((sample) => ({ x: sample.timeMs, y: sample.value })) ?? []));
        expect(timelineYDomain(tracks, counters)).toEqual({ yMin: expected.yMin, yMax: expected.yMax });
        expect(expected.yMin).toBeLessThanOrEqual(1);
        expect(expected.yMax).toBeGreaterThanOrEqual(900);
        expect(timelineYDomain([{ key: 'missing', color: '#fff' }], counters)).toEqual({ yMin: 0, yMax: 1 });
    });

    it('handles long millisecond series and duplicate tracks without overflowing the argument stack', () => {
        const samples = Array.from({ length: 250000 }, (_, index) => ({ timeMs: index, eventIndex: index, value: index === 200000 ? -40 : index === 240000 ? 800 : 5 }));
        samples[10].value = NaN;
        samples[11].value = Infinity;
        samples[12].value = -Infinity;
        const prepared: PreparedCounter = { samples, formatter: String, error: '' };
        const counters = new Map([['long', prepared], ['constant', counter([5, 5])], ['nonfinite', counter([NaN, Infinity, -Infinity])]]);
        const tracks = ['long', 'missing', 'constant', 'nonfinite', 'long'].map((key) => ({ key, color: '#fff' }));
        const { yMin, yMax } = getDataDomain([{ x: 0, y: -40 }, { x: 249999, y: 800 }]);
        expect(timelineYDomain(tracks, counters)).toEqual({ yMin, yMax });
        expect(prepared.samples).toBe(samples);
        expect(samples[10].value).toBeNaN();
        expect(samples[11].value).toBe(Infinity);
        expect(samples[12].value).toBe(-Infinity);
    });

    it('retains library padding for constant values and defaults when no finite value exists', () => {
        const counters = new Map([['constant', counter([5, 5, NaN])], ['nonfinite', counter([NaN, Infinity, -Infinity])]]);
        const expected = getDataDomain([{ x: 0, y: 5 }]);
        expect(timelineYDomain([{ key: 'constant', color: '#fff' }], counters)).toEqual({ yMin: expected.yMin, yMax: expected.yMax });
        expect(timelineYDomain([{ key: 'nonfinite', color: '#fff' }], counters)).toEqual({ yMin: 0, yMax: 1 });
        expect(timelineYDomain([], counters)).toEqual({ yMin: 0, yMax: 1 });
    });
});
