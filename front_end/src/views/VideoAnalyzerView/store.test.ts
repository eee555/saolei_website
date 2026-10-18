import { useLocalStorage } from '@vueuse/core';
import type { useStorage, UseStorageOptions } from '@vueuse/core';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { effectScope, nextTick } from 'vue';

import { analyzerConfig, defaultAnalyzerConfig } from './store';
import type { AnalyzerConfig } from './store';

import { parseCounterExpression } from '@/components/VideoAnalyzer/counter';
import { defaultCustomEvent } from '@/components/VideoAnalyzer/customEvents';
import { addTimelineTrack } from '@/components/VideoAnalyzer/timeline';

const storage = vi.hoisted(() => {
    const values = new Map<string, string>();
    return {
        getItem: (key: string) => values.get(key) ?? null,
        setItem: (key: string, value: string) => {
            values.set(key, value);
        },
        removeItem: (key: string) => {
            values.delete(key);
        },
    };
});

vi.mock('@vueuse/core', async (importOriginal) => {
    const actual = await importOriginal<{ useStorage: typeof useStorage }>();
    return {
        ...actual,
        useLocalStorage: (key: string, defaults: AnalyzerConfig, options: UseStorageOptions<AnalyzerConfig>) => actual.useStorage(key, defaults, storage, options),
    };
});

beforeEach(async () => {
    analyzerConfig.value = defaultAnalyzerConfig();
    await nextTick();
});

describe('analyzer settings storage', () => {
    it('removes retired export options while preserving the saved format, quality and other settings', async () => {
        storage.setItem('video-analyzer-config', JSON.stringify({ ...defaultAnalyzerConfig(), traceOpacity: 0.4, videoExport: { format: 'webm', fps: 60, quality: 'medium', parallelism: 4 } }));
        vi.resetModules();
        const { analyzerConfig: restored } = await import('./store');
        expect(restored.value.videoExport).toEqual({ format: 'webm', fps: 60, quality: 'medium' });
        expect(restored.value.traceOpacity).toBe(0.4);
        await nextTick();
        const saved = JSON.parse(storage.getItem('video-analyzer-config') ?? '{}') as AnalyzerConfig;
        expect(saved.videoExport).toEqual({ format: 'webm', fps: 60, quality: 'medium' });
    });

    it('defaults to left and right sustained events with the corresponding pressed mouse states', () => {
        const { customEvents } = defaultAnalyzerConfig();
        expect(customEvents.map(({ key, expression, type }) => ({ key, expression, type }))).toEqual([
            { key: 'left', expression: 'mouse_state in [4, 5, 6, 7]', type: 'sustained' },
            { key: 'right', expression: 'mouse_state in [2, 3, 5, 6]', type: 'sustained' },
        ]);
        for (const [index, states] of [[4, 5, 6, 7], [2, 3, 5, 6]].entries()) {
            const expression = parseCounterExpression(customEvents[index].expression);
            for (let mouseState = 1; mouseState <= 8; mouseState++) expect(expression.evaluate({ mouse_state: mouseState })).toBe(states.includes(mouseState));
        }
    });

    it('preserves saved empty counters, plots and custom events instead of restoring defaults', () => {
        const counter = { thWidth: 80, tdWidth: 96, rows: [] };
        const timeline = { slots: [[], []], slotSettings: [{ name: 'Custom', height: 240 }, { name: 'Other', height: 100 }] };
        storage.setItem('video-analyzer-config', JSON.stringify({ customEvents: [], counter, timeline }));
        const scope = effectScope();
        try {
            const restored = scope.run(() => useLocalStorage<AnalyzerConfig>('video-analyzer-config', defaultAnalyzerConfig(), { mergeDefaults: true }));
            expect(restored?.value.customEvents).toEqual([]);
            expect(restored?.value.counter).toEqual(counter);
            expect(restored?.value.timeline).toEqual(timeline);
        } finally {
            scope.stop();
        }
    });

    it('persists all editable settings and never includes replay-specific state', async () => {
        analyzerConfig.value.selectedLayout = 'counter-right';
        analyzerConfig.value.panelSizes['counter-right'].upper = [65, 35];
        analyzerConfig.value.globalVisible = true;
        analyzerConfig.value.probabilityVisible = false;
        analyzerConfig.value.globalOpacity = 0.4;
        analyzerConfig.value.probabilityOpacity = 0.7;
        analyzerConfig.value.traceVisible = true;
        analyzerConfig.value.traceOpacity = 0.6;
        analyzerConfig.value.traceTailSeconds = 'infinite';
        analyzerConfig.value.traceMaskOpacity = 0.25;
        analyzerConfig.value.traceAppearance.lineWidth = 0.15;
        analyzerConfig.value.traceAppearance.color.du = '#123456';
        analyzerConfig.value.traceAppearance.markers.lc.shape = 'square';
        analyzerConfig.value.traceAppearance.markers.lc.opacity = 0.4;
        analyzerConfig.value.traceAppearance.markers.rr.enabled = false;
        analyzerConfig.value.playbackRate = 2;
        analyzerConfig.value.loopMode = 'range';
        analyzerConfig.value.cellSizeMode = 'relative';
        analyzerConfig.value.fixedCellSize = 48;
        analyzerConfig.value.cellScale = 1.5;
        analyzerConfig.value.cursorVisible = false;
        analyzerConfig.value.cursorShape = 'windows';
        analyzerConfig.value.cursorSize = 40;
        analyzerConfig.value.eventLayer = { visible: true, keys: ['left'], timeRange: 'past', arrowSpacing: 48, arrowSize: 12, arrowShape: 'open' };
        analyzerConfig.value.videoExport = { format: 'webm', fps: 60, quality: 'medium' };
        analyzerConfig.value.counter.thWidth = 100;
        analyzerConfig.value.counter.tdWidth = 60;
        analyzerConfig.value.counter.rows[0].expression = 'path';
        analyzerConfig.value.counter.rows[0].format = '.1e';
        analyzerConfig.value.counter.rows[0].samplingMode = 'board';
        analyzerConfig.value.customEvents.push({ ...defaultCustomEvent(), key: 'pressed', expression: 'mouse_state == 4', color: '#123456', marker: { shape: 'diamond', size: 12, opacity: 0.6 } });
        addTimelineTrack(analyzerConfig.value.timeline, 0, 'bvs');
        addTimelineTrack(analyzerConfig.value.timeline, 0, 'bvs');
        analyzerConfig.value.timeline.slotSettings[0] = { name: 'Measurements', height: 240 };
        await nextTick();
        const raw = storage.getItem('video-analyzer-config');
        expect(raw).not.toBeNull();
        const saved = JSON.parse(raw ?? '{}') as AnalyzerConfig;
        expect(saved).toEqual(analyzerConfig.value);
        expect(saved.traceTailSeconds).toBe('infinite');
        for (const key of ['currentMs', 'durationMs', 'isPlaying', 'rangeStartMs', 'rangeEndMs', 'video', 'cursorPosition', 'timeWindow', 'hoverMs', 'preparedCounters', 'preparedEvents', 'crop', 'exporting']) expect(saved).not.toHaveProperty(key);
        expect(saved.timeline).toEqual({ slots: [[{ key: 'Bvs', color: '#4e79a7' }, { key: 'Ces', color: '#f28e2c' }, { key: 'bvs', color: '#e15759' }, { key: 'bvs', color: '#76b7b2' }], [{ key: 'Mov', color: '#4e79a7' }]], slotSettings: [{ name: 'Measurements', height: 240 }, { name: 'Plot 2', height: 160 }] });
    });

    it('restores saved settings through the storage reader, including unlimited tail', async () => {
        analyzerConfig.value.traceTailSeconds = 'infinite';
        analyzerConfig.value.playbackRate = 4;
        analyzerConfig.value.loopMode = 'all';
        analyzerConfig.value.cellSizeMode = 'fixed';
        analyzerConfig.value.fixedCellSize = 24;
        analyzerConfig.value.cellScale = 2;
        analyzerConfig.value.cursorShape = 'ring';
        analyzerConfig.value.cursorSize = 24;
        analyzerConfig.value.traceAppearance.markers.lr.size = 0.9;
        analyzerConfig.value.traceAppearance.markers.lr.enabled = false;
        analyzerConfig.value.counter.rows.push({ key: 'left', expression: 'left', format: '.0f', samplingMode: 'continuous' });
        addTimelineTrack(analyzerConfig.value.timeline, 1, 'missing-key');
        analyzerConfig.value.customEvents = [
            { ...defaultCustomEvent(), key: 'first', expression: 'left', type: 'sustained', line: { style: 'dash', width: 3, opacity: 0.4 } },
            { ...defaultCustomEvent(), key: 'second', expression: 'd(left)' },
        ];
        analyzerConfig.value.customEvents.reverse();
        analyzerConfig.value.customEvents[0].key = 'renamed';
        await nextTick();
        const scope = effectScope();
        try {
            const restored = scope.run(() => useLocalStorage<AnalyzerConfig>('video-analyzer-config', defaultAnalyzerConfig(), { mergeDefaults: true }));
            expect(restored?.value).toEqual(analyzerConfig.value);
        } finally {
            scope.stop();
        }
    });

    it('merges missing default fields and does not share panel arrays between defaults', () => {
        storage.setItem('video-analyzer-config', JSON.stringify({ selectedLayout: 'board-top', playbackRate: 2 }));
        const scope = effectScope();
        try {
            const restored = scope.run(() => useLocalStorage<AnalyzerConfig>('video-analyzer-config', defaultAnalyzerConfig(), { mergeDefaults: true }));
            expect(restored?.value).toEqual({ ...defaultAnalyzerConfig(), selectedLayout: 'board-top', playbackRate: 2 });
            expect(restored?.value.cellSizeMode).toBe('auto');
            expect(restored?.value.fixedCellSize).toBe(32);
            expect(restored?.value.cellScale).toBe(1);
            expect(restored?.value.cursorVisible).toBe(true);
            expect(restored?.value.cursorShape).toBe('dot');
            expect(restored?.value.cursorSize).toBe(32);
            expect(restored?.value.eventLayer).toEqual({ visible: false, keys: [], timeRange: 'all', arrowSpacing: 32, arrowSize: 8, arrowShape: 'triangle' });
            const first = defaultAnalyzerConfig();
            first.panelSizes['board-top'].outer[0] = 70;
            first.counter.rows[0].expression = 'time';
            first.counter.rows.push({ key: 'time', expression: 'time', format: '.3f', samplingMode: 'continuous' });
            first.timeline.slots[0].push({ key: 'bvs', color: '#fff' });
            first.timeline.slotSettings[0].name = 'Changed';
            first.traceAppearance.color.uu = '#123456';
            first.traceAppearance.markers.lc.enabled = false;
            first.customEvents[0].expression = 'false';
            first.customEvents[0].marker.size = 20;
            first.customEvents[0].line.width = 5;
            first.customEvents.push({ ...defaultCustomEvent(), key: 'event' });
            expect(defaultAnalyzerConfig().panelSizes['board-top'].outer[0]).toBe(50);
            expect(defaultAnalyzerConfig().counter.rows).toHaveLength(3);
            expect(defaultAnalyzerConfig().counter.rows[0].expression).toBe('d(bbbv_solved, 1000) / d(time, 1000)');
            expect(defaultAnalyzerConfig().timeline.slots.map((slot) => slot.map((track) => track.key))).toEqual([['Bvs', 'Ces'], ['Mov']]);
            expect(defaultAnalyzerConfig().timeline.slotSettings[0].name).toBe('Plot 1');
            expect(defaultAnalyzerConfig().traceAppearance.color.uu).toBe('#ffffff');
            expect(defaultAnalyzerConfig().traceAppearance.markers.lc.enabled).toBe(true);
            expect(defaultAnalyzerConfig().customEvents.map((event) => event.key)).toEqual(['left', 'right']);
            expect(defaultAnalyzerConfig().customEvents[0].expression).toBe('mouse_state in [4, 5, 6, 7]');
            expect(defaultAnalyzerConfig().customEvents[0].marker.size).toBe(8);
            expect(defaultAnalyzerConfig().customEvents[0].line.width).toBe(2);
            expect(first.customEvents[1].marker.size).toBe(8);
            expect(first.customEvents[1].line.width).toBe(2);
        } finally {
            scope.stop();
        }
    });
});
