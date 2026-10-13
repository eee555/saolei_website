import type { MouseTraceAction, MouseTraceState } from '@putianyi888/vue3-minesweeper-board';
import { bisector } from 'd3-array';
import type { VideoActionStateRecorder } from 'ms-toollib';

import type { ReplayMouseTraceEvent } from './mouseTrace';
import type { ReplayVideo } from './replayParser';

const byTime = bisector<ReplayMouseTraceEvent, number>((event) => event.timeMs);
const byIndex = bisector<ReplayMouseTraceEvent, number>((event) => event.eventIndex);

function mouseTraceState(state: number): MouseTraceState {
    if (state === 5 || state === 6) return 'dd';
    if (state === 4 || state === 7) return 'du';
    if (state === 2 || state === 3) return 'ud';
    return 'uu';
}

function mouseTraceAction(action: string): MouseTraceAction {
    return action === 'lc' || action === 'lr' || action === 'rc' || action === 'rr' ? action : 'mv';
}

export function readMouseTrace(video: ReplayVideo): ReplayMouseTraceEvent[] {
    const records = video.events as VideoActionStateRecorder[];
    const events: ReplayMouseTraceEvent[] = [];
    const pixelSize = video.pix_size;
    const startTime = video.video_start_time;
    try {
        records.forEach((record, eventIndex) => {
            const { event } = record;
            try {
                if (!event.is_mouse()) return;
                const mouse = event.unwrap_mouse();
                try {
                    events.push({
                        row: mouse.y / pixelSize,
                        column: mouse.x / pixelSize,
                        state: mouseTraceState(record.mouse_state),
                        action: mouseTraceAction(mouse.mouse),
                        timeMs: (record.time + startTime) * 1000,
                        eventIndex,
                    });
                } finally {
                    mouse.free();
                }
            } finally {
                event.free();
            }
        });
    } finally {
        for (const record of records) record.free();
    }
    return events;
}

export function mouseTraceRange(events: ReplayMouseTraceEvent[], currentMs: number, tailSeconds: number, currentEventIndex: number | null = null): { startIndex: number; endIndex: number } {
    const endIndex = currentEventIndex === null ? byTime.right(events, currentMs) : byIndex.right(events, currentEventIndex);
    if (tailSeconds === Infinity || endIndex === 0) return { startIndex: 0, endIndex };
    const leftTime = Math.max(0, currentMs - tailSeconds * 1000);
    const leftEvent = events[byTime.right(events, leftTime) - 1];
    // Include the complete timestamp group on the left, even when it precedes the window.
    const startIndex = leftEvent === undefined ? 0 : byTime.left(events, leftEvent.timeMs);
    return { startIndex: Math.min(startIndex, endIndex), endIndex };
}

