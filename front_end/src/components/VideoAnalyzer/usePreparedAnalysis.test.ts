import { describe, expect, it } from 'vitest';
import { ref, shallowRef } from 'vue';

import { defaultAnalyzerConfig } from './config';
import { counterVariables } from './counter';
import type { CounterEvent, CounterValues } from './counter';
import { usePreparedAnalysis } from './usePreparedAnalysis';

function setup() {
    const config = ref(defaultAnalyzerConfig());
    config.value.counter.rows = [{ key: 'time', expression: 'time', format: '.3f', samplingMode: 'continuous' }];
    config.value.customEvents = [{ ...config.value.customEvents[0], key: 'left', expression: 'left > 0' }];
    const values = Object.fromEntries(counterVariables.map((key) => [key, 0])) as CounterValues;
    const events = shallowRef<CounterEvent[]>([
        { timeMs: 0, eventIndex: 0, button: true, boardChanged: false, values },
        { timeMs: 10, eventIndex: 1, button: true, boardChanged: true, values: { ...values, time: 0.01, left: 1 } },
    ]);
    const durationMs = ref(20);
    return { config, events, durationMs, ...usePreparedAnalysis(config, events, durationMs) };
}

describe('VideoAnalyzer sampling invalidation', () => {
    it('reuses full-replay samples for layer edits and unrelated root-config replacements', () => {
        const { config, preparedCounters, preparedEvents } = setup();
        const counters = preparedCounters.value;
        const events = preparedEvents.value;
        config.value.globalVisible = true;
        config.value.probabilityOpacity = 0.25;
        config.value.traceAppearance.lineWidth = 0.1;
        config.value.eventLayer.visible = true;
        config.value.eventLayer.keys.push('left');
        config.value = { ...config.value, cursorSize: 20 };
        expect(preparedCounters.value).toBe(counters);
        expect(preparedEvents.value).toBe(events);
    });

    it('recomputes only the affected analysis when expressions or definitions change', () => {
        const { config, preparedCounters, preparedEvents } = setup();
        const counters = preparedCounters.value;
        const events = preparedEvents.value;
        config.value.counter.rows[0].expression = 'left';
        const changedCounters = preparedCounters.value;
        expect(changedCounters).not.toBe(counters);
        expect(changedCounters.get('time')?.samples.at(-1)?.value).toBe(1);
        expect(preparedEvents.value).toBe(events);
        config.value.customEvents[0].expression = 'left > 1';
        expect(preparedEvents.value).not.toBe(events);
        expect(preparedEvents.value.get('left')?.spans).toEqual([]);
        expect(preparedCounters.value).toBe(changedCounters);
        config.value = { ...config.value, counter: { ...config.value.counter, rows: [{ ...config.value.counter.rows[0], expression: 'left + 2' }] } };
        expect(preparedCounters.value.get('time')?.samples.at(-1)?.value).toBe(3);
        config.value = { ...config.value, customEvents: [] };
        expect(preparedEvents.value.size).toBe(0);
    });

    it('updates both analyses when replay events or duration change', () => {
        const { events, durationMs, preparedCounters, preparedEvents } = setup();
        const counters = preparedCounters.value;
        const customEvents = preparedEvents.value;
        durationMs.value = 30;
        expect(preparedCounters.value).not.toBe(counters);
        expect(preparedCounters.value.get('time')?.samples.at(-1)?.timeMs).toBe(30);
        expect(preparedEvents.value).not.toBe(customEvents);
        expect(preparedEvents.value.get('left')?.spans[0].endMs).toBe(30);
        events.value = [];
        expect(preparedCounters.value.get('time')?.samples).toEqual([]);
        expect(preparedEvents.value.get('left')?.spans).toEqual([]);
    });
});
