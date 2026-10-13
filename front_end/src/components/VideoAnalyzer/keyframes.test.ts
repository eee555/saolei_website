import { describe, expect, it } from 'vitest';

import { counterVariables } from './counter';
import type { CounterEvent, CounterValues } from './counter';
import { adjacentKeyframe } from './keyframes';

const keyframes: CounterEvent[] = [2, 5, 8].map((eventIndex) => ({
    eventIndex,
    timeMs: 1000,
    button: true,
    boardChanged: false,
    values: Object.fromEntries(counterVariables.map((key) => [key, 0])) as CounterValues,
}));

describe('adjacent keyframes', () => {
    it('uses strict original event order rather than timestamp and skips the current frame', () => {
        expect(adjacentKeyframe(keyframes, 5, -1)).toBe(keyframes[0]);
        expect(adjacentKeyframe(keyframes, 5, 1)).toBe(keyframes[2]);
        expect(adjacentKeyframe(keyframes, 6, -1)).toBe(keyframes[1]);
        expect(adjacentKeyframe(keyframes, 6, 1)).toBe(keyframes[2]);
        expect(keyframes.map((event) => event.eventIndex)).toEqual([2, 5, 8]);
    });

    it('returns no frame at a missing boundary or without a current event', () => {
        expect(adjacentKeyframe(keyframes, 2, -1)).toBeUndefined();
        expect(adjacentKeyframe(keyframes, 8, 1)).toBeUndefined();
        expect(adjacentKeyframe([], 0, 1)).toBeUndefined();
        expect(adjacentKeyframe(keyframes, null, -1)).toBeUndefined();
    });
});
