import { describe, expect, it } from 'vitest';

import { boardEventGeometry, defaultBoardEventSettings, eventDirectionArrows, updateBoardEventKeys } from './boardEvents';
import { defaultCustomEvent } from './customEvents';
import type { PreparedCustomEvent } from './customEvents';
import type { ReplayMouseTraceEvent } from './mouseTrace';

const definitions = [{ ...defaultCustomEvent(), key: 'click' }, { ...defaultCustomEvent(), key: 'held', type: 'sustained' as const }];
const mouse: ReplayMouseTraceEvent[] = [
    { row: 0, column: 0, timeMs: 0, eventIndex: 0, action: 'mv', state: 'uu' },
    { row: 1, column: 1, timeMs: 10, eventIndex: 1, action: 'lc', state: 'du' },
    { row: 1, column: 2, timeMs: 10, eventIndex: 2, action: 'mv', state: 'du' },
    { row: 2, column: 2, timeMs: 20, eventIndex: 3, action: 'mv', state: 'du' },
    { row: 3, column: 2, timeMs: 30, eventIndex: 4, action: 'lr', state: 'uu' },
];
const prepared = new Map<string, PreparedCustomEvent>([
    ['click', { pulses: [{ timeMs: 10, eventIndex: 2, value: 0.25 }, { timeMs: 30, eventIndex: 4 }], spans: [] }],
    ['held', { pulses: [], spans: [{ startMs: 10, endMs: 30, renderEndMs: 20, startEventIndex: 2, lastEventIndex: 3 }] }],
]);

describe('board custom event geometry', () => {
    it('defaults to visible pluck, global range and independent arrow settings', () => {
        expect(defaultBoardEventSettings()).toEqual({ visible: true, keys: ['pluck'], timeRange: 'all', arrowSpacing: 32, arrowSize: 8, arrowShape: 'triangle' });
        const first = defaultBoardEventSettings();
        first.keys.push('click');
        expect(defaultBoardEventSettings().keys).toEqual(['pluck']);
        expect(boardEventGeometry(definitions, prepared, mouse, [])).toEqual([]);
    });

    it('keeps all native points including the first millisecond group, excluding the first false sample', () => {
        const result = boardEventGeometry(definitions, prepared, mouse, ['held', 'click']);
        expect(result[0].pulses.map(({ x, y }) => ({ x, y }))).toEqual([{ x: 2, y: 1 }, { x: 2, y: 3 }]);
        expect(result[0].pulses[0].pulse).toBe(prepared.get('click')?.pulses[0]);
        expect(result[0].pulses[0].pulse.value).toBe(0.25);
        expect(result[0].pulses[1].pulse.value).toBeUndefined();
        expect(result[1].paths.map((path) => path.points)).toEqual([[{ x: 1, y: 1 }, { x: 2, y: 1 }, { x: 2, y: 2 }]]);
        const clipped = boardEventGeometry(definitions, prepared, mouse, ['held'], 15)[0].paths;
        expect(clipped.map((path) => path.points)).toEqual([[{ x: 1, y: 1 }, { x: 2, y: 1 }]]);
        expect(clipped[0].span).toBe(prepared.get('held')?.spans[0]);
        expect(boardEventGeometry(definitions, prepared, mouse, ['held'], 10, 1)[0].paths.map((path) => path.points)).toEqual([[{ x: 1, y: 1 }]]);
        expect(boardEventGeometry(definitions, prepared, mouse, ['click'], 10, 1)[0].pulses).toEqual([]);
        expect(boardEventGeometry(definitions, prepared, mouse, ['held'], 9)[0].paths).toEqual([]);
    });

    it('matches millisecond snapshots despite floating-point seconds conversion', () => {
        const rounded = mouse.map((event) => ({ ...event, timeMs: event.timeMs + (event.eventIndex === 1 ? -1e-10 : 1e-10) }));
        expect(boardEventGeometry(definitions, prepared, rounded, ['click', 'held'], 20)).toEqual(boardEventGeometry(definitions, prepared, mouse, ['click', 'held'], 20));
    });

    it('skips missing pulse positions and breaks paths at invalid coordinates without bridging gaps', () => {
        const missing = new Map<string, PreparedCustomEvent>([['click', { pulses: [{ timeMs: 20, eventIndex: 10 }], spans: [] }]]);
        expect(boardEventGeometry(definitions, missing, mouse, ['click'])[0].pulses).toEqual([]);
        const invalid = mouse.map((event) => ({ ...event, column: event.eventIndex === 2 ? NaN : event.column }));
        const split = boardEventGeometry(definitions, prepared, invalid, ['held'])[0].paths;
        expect(split.map((path) => path.points)).toEqual([[{ x: 1, y: 1 }], [{ x: 2, y: 2 }]]);
        for (const path of split) expect(path.span).toBe(prepared.get('held')?.spans[0]);
        expect(boardEventGeometry(definitions, prepared, mouse, ['deleted'])).toEqual([]);
    });

    it('updates selection references on rename and removal, preserving order', () => {
        expect(updateBoardEventKeys(['click', 'held'], 'held', 'renamed')).toEqual(['click', 'renamed']);
        expect(updateBoardEventKeys(['click', 'held'], 'click', null)).toEqual(['held']);
    });

    it('places arrows along pixel arc length and preserves direction through corners and stationary points', () => {
        const points = [{ x: 0, y: 0 }, { x: 32, y: 0 }, { x: 32, y: 0 }, { x: 32, y: 64 }];
        expect(eventDirectionArrows(points, 32)).toEqual([{ x: 32, y: 0, angle: 0 }, { x: 32, y: 32, angle: 90 }, { x: 32, y: 64, angle: 90 }]);
        expect(eventDirectionArrows([{ x: 3, y: 4 }, { x: 0, y: 4 }], 32)).toEqual([{ x: 0, y: 4, angle: 180 }]);
        expect(eventDirectionArrows([{ x: 0, y: 0 }, { x: 0, y: 0 }], 32)).toEqual([]);
        for (const spacing of [0, 0.5, -1, NaN, Infinity]) expect(eventDirectionArrows(points, spacing)).toEqual([]);
    });
});
