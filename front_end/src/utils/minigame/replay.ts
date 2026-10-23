import { defaultMouseTraceMarkers, mouseTraceMarkerActions } from '@putianyi888/vue3-minesweeper-board';
import type { MouseTraceEvent, MouseTraceMarkers } from '@putianyi888/vue3-minesweeper-board';
import { bisector } from 'd3-array';

import type { ClassicMouseAction, ClassicMouseEvent } from '../classicMouse';

import type { BoardPress } from './boardPress';
import type { TrainingPhase } from './clock';

// Internal observations shared by live replay and IndexedDB history; not an export format.
export interface TrainingMouseInput {
    now: number;
    action: ClassicMouseEvent | null;
    row: number;
    column: number;
    state: MouseTraceEvent['state'];
    pressed: BoardPress | null;
    trigger: ClassicMouseAction | null;
}

export interface TrainingReplayEvent extends MouseTraceEvent {
    timeMs: number;
    pressed: BoardPress | null;
    trigger: ClassicMouseAction | null;
    cancelled: boolean;
}

interface ReplaySnapshot {
    eventIndex: number;
    board: number[][];
    remaining: number;
}

export interface FlagChordTiming {
    flagMs: number;
    leftMs: number;
    chordMs: number;
    eventIndex: number;
}

export interface TrainingReplay {
    durationMs: number;
    events: TrainingReplayEvent[];
    snapshots: ReplaySnapshot[];
    chords: FlagChordTiming[];
}

export interface ReplayPosition {
    timeMs: number;
    eventIndex?: number;
}

export interface TrainingReplayFrame extends ReplaySnapshot {
    timeMs: number;
    pressed: BoardPress | null;
    cursor: { rowIndex: number; columnIndex: number } | undefined;
}

export const minigameReplayAppearance = {
    opacity: 0,
    lineWidth: 0.08,
    markers: Object.fromEntries(mouseTraceMarkerActions.map((action) => [action, { ...defaultMouseTraceMarkers[action], size: 0.25 }])) as MouseTraceMarkers,
};

export class TrainingReplayRecorder {
    private startedAt: number | null = null;
    private finished = false;
    private pending: TrainingMouseInput | null = null;
    private readonly events: TrainingReplayEvent[] = [];
    private readonly snapshots: ReplaySnapshot[];
    private readonly flags = new Map<number, number>();
    private readonly chords: FlagChordTiming[] = [];

    public constructor(board: number[][], remaining: number) {
        this.snapshots = [{ eventIndex: -1, board, remaining }];
    }

    public capture(input: TrainingMouseInput): void {
        if (this.finished) return;
        this.pending = input;
        if (this.startedAt === null) return;
        this.events.push({
            timeMs: Math.max(0, Math.round(input.now - this.startedAt)),
            action: input.action ?? 'mv',
            row: input.row,
            column: input.column,
            state: input.state,
            pressed: input.pressed,
            trigger: input.trigger,
            cancelled: input.action === null,
        });
    }

    public update(now: number, board: number[][], remaining: number, phase: TrainingPhase, durationMs: number): TrainingReplay | null {
        if (this.finished || phase === 'ready') return null;
        if (this.startedAt === null) {
            this.startedAt = now;
            if (this.pending !== null) this.capture({ ...this.pending, now });
        }
        this.snapshots.push({ eventIndex: this.events.length - 1, board, remaining });
        if (phase === 'playing') return null;
        this.finished = true;
        return { durationMs, events: this.events, snapshots: this.snapshots, chords: this.chords };
    }

    /** Called only after the game accepts a flag placement. */
    public flag(question: number): void {
        const event = this.events.at(-1);
        if (event !== undefined) this.flags.set(question, event.timeMs);
    }

    /** Called only when this chord completes a question, never for failed/no-op chords. */
    public completeQuestion(question: number): void {
        const flagMs = this.flags.get(question);
        const eventIndex = this.events.length - 1;
        const chord = this.events[eventIndex];
        if (flagMs === undefined || chord === undefined) return;
        for (let index = eventIndex - 1; index >= 0; index--) {
            const event = this.events[index];
            if (event.cancelled || event.timeMs < flagMs) return;
            if (event.action === 'lc') {
                this.chords.push({ flagMs, leftMs: event.timeMs, chordMs: chord.timeMs, eventIndex });
                return;
            }
        }
    }
}

const eventTime = bisector<TrainingReplayEvent, number>((event) => event.timeMs);
const snapshotIndex = bisector<ReplaySnapshot, number>((snapshot) => snapshot.eventIndex);

export function replayFrame(replay: TrainingReplay, position: ReplayPosition): TrainingReplayFrame {
    const timeMs = Math.max(0, Math.min(replay.durationMs, position.timeMs));
    const eventIndex = position.eventIndex ?? eventTime.right(replay.events, timeMs) - 1;
    const event = replay.events[eventIndex];
    const snapshot = replay.snapshots[Math.max(0, snapshotIndex.right(replay.snapshots, eventIndex) - 1)];
    return {
        ...snapshot,
        timeMs,
        eventIndex,
        pressed: event?.pressed ?? null,
        cursor: event === undefined ? undefined : { rowIndex: event.row, columnIndex: event.column },
    };
}
