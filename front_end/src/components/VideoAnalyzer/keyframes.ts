import { bisector } from 'd3-array';

import type { CounterEvent } from './counter';

export interface KeyframeNavigation {
    previous: () => void;
    next: () => void;
}

const byIndex = bisector<CounterEvent, number>((event) => event.eventIndex);

export function adjacentKeyframe(keyframes: CounterEvent[], currentEventIndex: number | null, direction: -1 | 1): CounterEvent | undefined {
    if (currentEventIndex === null) return undefined;
    const index = direction === -1 ? byIndex.left(keyframes, currentEventIndex) - 1 : byIndex.right(keyframes, currentEventIndex);
    return keyframes[index];
}
