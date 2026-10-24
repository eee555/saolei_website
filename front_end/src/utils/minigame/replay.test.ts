import { describe, expect, it, vi } from 'vitest';

import { flagChordModes, FlagChordTraining } from './flagChordTraining';
import { leftClickModes, LeftClickTraining } from './leftClickTraining';
import { minigameReplayAppearance, rebuildTrainingReplay, replayFrame, TrainingReplayRecorder } from './replay';
import type { TrainingMouseInput, TrainingReplay } from './replay';
import { clickDurationBins, leftClickDurations, replaySpeeds } from './replayAnalysis';

function input(now: number, action: TrainingMouseInput['action'], trigger: TrainingMouseInput['trigger'] = null, column = 0.5, row = 0.5): TrainingMouseInput {
    return { now, action, trigger, row, column, state: action === 'lc' ? 'du' : action === 'rc' ? 'ud' : 'uu', pressed: action === 'lc' ? { row: Math.floor(row), column: Math.floor(column), chord: false } : null };
}

function leftBoard(): number[][] {
    return Array.from({ length: 8 }, (_, row) => Array.from({ length: 8 }, () => (row < 4 ? 10 : 16)));
}

function flagBoard(): number[][] {
    const board = Array.from({ length: 8 }, () => Array.from({ length: 8 }, () => 0));
    for (const row of [1, 5]) {
        for (const column of [1, 5]) {
            for (let r = row - 1; r <= row + 1; r++) {
                for (let c = column - 1; c <= column + 1; c++) board[r][c] = 10;
            }
            board[row][column] = 1;
            board[row - 1][column - 1] = 16;
        }
    }
    return board;
}

describe('in-memory minigame replay', () => {
    it('rebuilds every accepted action from the initial board, restores seeks, and freezes at completion', () => {
        const board = leftBoard();
        const game = new LeftClickTraining(leftClickModes[0], undefined, board);
        const recorder = new TrainingReplayRecorder('left-click', board);
        const expectedBoards = [game.board];
        recorder.capture(input(10, 'lc'));
        recorder.capture(input(100, 'lr', 'left'));
        game.trigger(0, 0, 100);
        expectedBoards.push(game.board);
        expect(recorder.update(100, game.phase, 0)).toBeNull();
        recorder.capture(input(150, 'lc', null, 1.25));
        recorder.capture(input(200, 'lr', 'left', 1.75));
        game.trigger(0, 1, 200);
        expectedBoards.push(game.board);
        recorder.update(200, game.phase, 100);
        // Clicking an already opened cell remains an event but must not add a snapshot.
        recorder.capture(input(210, 'lr', 'left', 1.75));
        for (let index = 2; index < 32; index++) {
            const now = 200 + index * 50;
            recorder.capture(input(now, 'lr', 'left', index % 8 + 0.5, Math.floor(index / 8) + 0.5));
            game.trigger(Math.floor(index / 8), index % 8, now);
            expectedBoards.push(game.board);
        }
        const random = vi.spyOn(Math, 'random').mockImplementation(() => {
            throw new Error('Replay must not draw another board');
        });
        let replay: TrainingReplay | null;
        try {
            replay = recorder.update(1750, game.phase, game.elapsedMs(1750));
        } finally {
            random.mockRestore();
        }
        if (replay === null) throw new Error('Missing replay');
        expect(replay.events.slice(0, 3).map((event) => event.timeMs)).toEqual([0, 50, 100]);
        expect(replay.snapshots).toHaveLength(33);
        expect(replay.snapshots.map((snapshot) => snapshot.board)).toEqual(expectedBoards);
        expect(replayFrame(replay, { timeMs: replay.durationMs })).toMatchObject({ board: game.board, remaining: 0, pressed: null });
        expect(replayFrame(replay, { timeMs: 75 })).toMatchObject({ remaining: 31, pressed: { column: 1, chord: false }, cursor: { columnIndex: 1.25 } });
        expect(replayFrame(replay, { timeMs: 100 }).board[0].slice(0, 3)).toEqual([0, 0, 10]);
        expect(replayFrame(replay, { timeMs: 0 })).toMatchObject({ remaining: 31, eventIndex: 0 });
        expect(replayFrame(replay, { timeMs: 0, eventIndex: -1 }).board).toEqual(board);
        recorder.capture(input(9999, 'mv'));
        expect(replay.events).toHaveLength(34);
        expect(minigameReplayAppearance.opacity).toBe(0);
        expect(Object.values(minigameReplayAppearance.markers).map((marker) => (marker === false ? null : marker.size))).toEqual([0.25, 0.25, 0.25, 0.25]);
    });

    it('derives the last corrected flag and the left press before a successful chord, excluding failed chords', () => {
        const recorder = new TrainingReplayRecorder('flag-chord', flagBoard());
        recorder.capture(input(100, 'rc', 'right', 1.5));
        recorder.update(100, 'playing', 0);
        for (const event of [
            input(150, 'rr', null, 1.5), input(160, 'rc', 'right', 1.5), input(170, 'rr', null, 1.5),
            input(200, 'rc', 'right'), input(210, 'rr'), input(250, 'lc', null, 1.5, 1.5),
            input(260, 'rc', null, 1.5, 1.5), input(300, 'lr', 'chord', 1.5, 1.5),
            input(310, 'rr'), input(400, 'rc', 'right', 5.5), input(410, 'rr'),
            input(450, 'lc', null, 5.5, 1.5), input(460, 'rc', null, 5.5, 1.5), input(500, 'lr', 'chord', 5.5, 1.5),
        ]) recorder.capture(event);
        const replay = recorder.update(500, 'lost', 400);
        if (replay === null) throw new Error('Missing replay');
        expect(replay.chords).toEqual([{ flagMs: 100, leftMs: 150, chordMs: 200, eventIndex: 8 }]);
        expect(replayFrame(replay, { timeMs: 400 }).board[0][4]).toBe(15);
        expect(replayFrame(replay, { timeMs: 200 }).remaining).toBe(3);
        const restored = rebuildTrainingReplay('flag-chord', { initialBoard: replay.initialBoard, events: replay.events }, replay.durationMs);
        expect(restored.snapshots).toEqual(replay.snapshots);
        expect(restored.chords).toEqual(replay.chords);
    });

    it('can select a particular event among observations with the same millisecond timestamp', () => {
        const recorder = new TrainingReplayRecorder('flag-chord', flagBoard());
        recorder.capture(input(0, 'rc', 'right'));
        recorder.update(0, 'playing', 0);
        recorder.capture(input(1, 'lc', null, 1.5, 1.5));
        recorder.capture(input(1, 'lr', 'chord', 1.5, 1.5));
        recorder.capture(input(1, 'rr', null, 2.5, 1.5));
        const replay = recorder.update(1, 'won', 1);
        if (replay === null) throw new Error('Missing replay');
        expect(replayFrame(replay, { timeMs: 1, eventIndex: replay.chords[0].eventIndex }).cursor?.columnIndex).toBe(1.5);
        expect(replayFrame(replay, { timeMs: 1 }).cursor?.columnIndex).toBe(2.5);
    });

    it('computes distance and click counts over a trailing one-second window, including partial movement segments', () => {
        const recorder = new TrainingReplayRecorder('left-click', leftBoard());
        recorder.capture(input(0, 'lr', 'left'));
        recorder.update(0, 'playing', 0);
        recorder.capture(input(2000, 'mv', null, 4.5));
        const replay = recorder.update(2000, 'won', 2000);
        if (replay === null) throw new Error('Missing replay');
        const samples = replaySpeeds(replay);
        expect(samples.find((sample) => sample.timeMs === 500)).toEqual({ timeMs: 500, mouseSpeed: 1, clickSpeed: 1 });
        expect(samples.find((sample) => sample.timeMs === 1000)).toEqual({ timeMs: 1000, mouseSpeed: 2, clickSpeed: 0 });
        expect(samples.at(-1)).toEqual({ timeMs: 2000, mouseSpeed: 2, clickSpeed: 0 });
    });

    it('excludes the initial click, cancelled presses and chords from the click-duration histogram', () => {
        const recorder = new TrainingReplayRecorder('left-click', leftBoard());
        recorder.capture(input(0, 'lr', 'left'));
        recorder.update(0, 'playing', 0);
        for (const event of [input(10, 'lc'), input(50, 'lr', 'left'), input(60, 'lc'), input(80, null), input(90, 'lr', 'left'), input(100, 'lc'), input(110, 'lr', 'chord'), input(120, 'lc'), input(150, 'lr', 'left')]) recorder.capture(event);
        const replay = recorder.update(150, 'won', 150);
        if (replay === null) throw new Error('Missing replay');
        expect(leftClickDurations(replay)).toEqual([40, 30]);
        const bins = clickDurationBins(replay);
        expect(bins.reduce((total, item) => total + item.length, 0)).toBe(2);
        expect(bins.map((item) => [item.x0, item.x1, item.length])).toEqual([
            [0, 10, 0], [10, 20, 0], [20, 30, 0], [30, 40, 1], [40, 50, 1],
        ]);
    });

    it.each(flagChordModes)('rebuilds every board and timing for $key without generating new positions', (mode) => {
        const live = new FlagChordTraining(mode, () => 0.37);
        const { board } = live;
        const recorder = new TrainingReplayRecorder('flag-chord', board);
        const expectedBoards = [board];
        live.questions.forEach((question, index) => {
            const now = 100 + index * 100;
            const row = Math.floor(question.mine / mode.columns);
            const column = question.mine % mode.columns;
            recorder.capture(input(now, 'rc', 'right', column + 0.5, row + 0.5));
            live.act('right', row, column, now);
            recorder.update(now, live.phase, live.elapsedMs(now));
            expectedBoards.push(live.board);
            recorder.capture(input(now + 20, 'lc', null, question.column + 0.5, question.row + 0.5));
            recorder.capture(input(now + 40, 'lr', 'chord', question.column + 0.5, question.row + 0.5));
            live.act('chord', question.row, question.column, now + 40);
            expectedBoards.push(live.board);
        });
        const replay = recorder.update(100 + mode.total * 100, live.phase, live.elapsedMs(99999));
        if (replay === null) throw new Error('Missing replay');
        expect(replay.snapshots.map((snapshot) => snapshot.board)).toEqual(expectedBoards);
        expect(replay.chords).toEqual(Array.from({ length: mode.total }, (_, index) => ({ flagMs: index * 100, leftMs: index * 100 + 20, chordMs: index * 100 + 40, eventIndex: index * 3 + 2 })));
        expect(replayFrame(replay, { timeMs: replay.durationMs })).toMatchObject({ board: live.board, remaining: 0 });
    });
});
