import { defaultMouseTraceMarkers, mouseTraceMarkerActions } from '@putianyi888/vue3-minesweeper-board';
import type { MouseTraceEvent, MouseTraceMarkers } from '@putianyi888/vue3-minesweeper-board';
import { bisector } from 'd3-array';

import type { ClassicMouseAction, ClassicMouseEvent } from '../classicMouse';

import type { BoardPress } from './boardPress';
import type { TrainingPhase } from './clock';
import { flagChordModes, FlagChordTraining } from './flagChordTraining';
import { leftClickModes, LeftClickTraining } from './leftClickTraining';

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

/** Only the source data is persisted; frames and timings are derived during review. */
export interface TrainingRecording {
    initialBoard: number[][];
    events: TrainingReplayEvent[];
}

export interface TrainingReplay extends TrainingRecording {
    game: 'left-click' | 'flag-chord';
    durationMs: number;
    snapshots: ReplaySnapshot[];
    chords: FlagChordTiming[];
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
    private readonly game: TrainingReplay['game'];
    private readonly initialBoard: number[][];

    public constructor(game: TrainingReplay['game'], initialBoard: number[][]) {
        this.game = game;
        this.initialBoard = initialBoard;
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

    public update(now: number, phase: TrainingPhase, durationMs: number): TrainingReplay | null {
        if (this.finished || phase === 'ready') return null;
        if (this.startedAt === null) {
            this.startedAt = now;
            if (this.pending !== null) this.capture({ ...this.pending, now });
        }
        if (phase === 'playing') return null;
        this.finished = true;
        return rebuildTrainingReplay(this.game, { initialBoard: this.initialBoard, events: this.events }, durationMs);
    }
}

function createReplayGame(replay: Pick<TrainingReplay, 'game' | 'initialBoard'>): LeftClickTraining | FlagChordTraining {
    const board = replay.initialBoard;
    const rows = board.length;
    const columns = board[0]?.length ?? 0;
    if (replay.game === 'left-click') {
        const mines = board.flat().filter((value) => value === 16).length;
        const mode = leftClickModes.find((item) => item.rows === rows && item.columns === columns && item.mines === mines);
        if (mode === undefined) throw new Error('Unknown left-click replay mode');
        return new LeftClickTraining(mode, Math.random, board);
    }
    const mode = flagChordModes.find((item) => item.rows === rows && item.columns === columns);
    if (mode === undefined) throw new Error('Unknown flag-and-chord replay mode');
    return new FlagChordTraining(mode, Math.random, board);
}

function applyEvent(game: LeftClickTraining | FlagChordTraining, event: TrainingReplayEvent): boolean {
    if (event.cancelled || event.trigger === null) return false;
    const row = Math.floor(event.row);
    const column = Math.floor(event.column);
    return game instanceof LeftClickTraining ? event.trigger === 'left' && game.trigger(row, column, event.timeMs) : game.act(event.trigger, row, column, event.timeMs);
}

const eventTime = bisector<TrainingReplayEvent, number>((event) => event.timeMs);
const snapshotIndex = bisector<ReplaySnapshot, number>((snapshot) => snapshot.eventIndex);

/** Expand source data once when opening a replay; derived data stays in memory. */
export function rebuildTrainingReplay(kind: TrainingReplay['game'], recording: TrainingRecording, durationMs: number): TrainingReplay {
    const game = createReplayGame({ game: kind, initialBoard: recording.initialBoard });
    const remaining = () => (game instanceof LeftClickTraining ? game.remainingSafe : game.remaining);
    const snapshots: ReplaySnapshot[] = [{ eventIndex: -1, board: game.board, remaining: remaining() }];
    const chords: FlagChordTiming[] = [];
    const flags = new Map<number, number>();
    let leftMs: number | null = null;
    recording.events.forEach((event, eventIndex) => {
        if (event.cancelled) leftMs = null;
        else if (event.action === 'lc') leftMs = event.timeMs;
        const previousRemaining = remaining();
        if (!applyEvent(game, event)) return;
        const { board } = game;
        snapshots.push({ eventIndex, board, remaining: remaining() });
        if (!(game instanceof FlagChordTraining)) return;
        const row = Math.floor(event.row);
        const column = Math.floor(event.column);
        const question = game.questions.findIndex((item) => Math.abs(item.row - row) <= 1 && Math.abs(item.column - column) <= 1);
        if (event.trigger === 'right' && board[row][column] === 11) flags.set(question, event.timeMs);
        const flagMs = flags.get(question);
        if (game.remaining < previousRemaining && flagMs !== undefined && leftMs !== null && leftMs >= flagMs) chords.push({ flagMs, leftMs, chordMs: event.timeMs, eventIndex });
    });
    return { ...recording, game: kind, durationMs, snapshots, chords };
}

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
