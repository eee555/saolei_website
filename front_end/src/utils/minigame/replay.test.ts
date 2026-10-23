import { describe, expect, it } from 'vitest';

import { minigameReplayAppearance, replayFrame, TrainingReplayRecorder } from './replay';
import type { TrainingMouseInput } from './replay';
import { clickDurationBins, leftClickDurations, replaySpeeds } from './replayAnalysis';

function input(now: number, action: TrainingMouseInput['action'], trigger: TrainingMouseInput['trigger'] = null, column = 0.5): TrainingMouseInput {
    return { now, action, trigger, row: 0.5, column, state: action === 'lc' ? 'du' : action === 'rc' ? 'ud' : 'uu', pressed: action === 'lc' ? { row: 0, column: Math.floor(column), chord: false } : null };
}

describe('in-memory minigame replay', () => {
    it('starts at the timed action, restores past board/counter/press/cursor states, and freezes at completion', () => {
        const recorder = new TrainingReplayRecorder([[10, 10]], 2);
        recorder.capture(input(10, 'lc'));
        recorder.capture(input(100, 'lr', 'left'));
        expect(recorder.update(100, [[0, 10]], 1, 'playing', 0)).toBeNull();
        recorder.capture(input(150, 'lc', null, 1.25));
        recorder.capture(input(200, 'lr', 'left', 1.75));
        const replay = recorder.update(200, [[0, 0]], 0, 'won', 100);
        if (replay === null) throw new Error('Missing replay');
        expect(replay.events.map((event) => event.timeMs)).toEqual([0, 50, 100]);
        expect(replayFrame(replay, { timeMs: 75 })).toMatchObject({ board: [[0, 10]], remaining: 1, pressed: { column: 1, chord: false }, cursor: { columnIndex: 1.25 } });
        expect(replayFrame(replay, { timeMs: 100 })).toMatchObject({ board: [[0, 0]], remaining: 0, pressed: null });
        expect(replayFrame(replay, { timeMs: 0 })).toMatchObject({ board: [[0, 10]], remaining: 1, eventIndex: 0 });
        recorder.capture(input(300, 'mv'));
        expect(replay.events).toHaveLength(3);
        expect(minigameReplayAppearance.opacity).toBe(0);
        expect(Object.values(minigameReplayAppearance.markers).map((marker) => (marker === false ? null : marker.size))).toEqual([0.25, 0.25, 0.25, 0.25]);
    });

    it('uses the last flag after correcting a mistake, even after releasing right and pressing left first', () => {
        const recorder = new TrainingReplayRecorder([[10, 16, 1]], 1);
        recorder.capture(input(100, 'rc', 'right'));
        recorder.update(100, [[11, 16, 1]], 1, 'playing', 0);
        recorder.flag(0);
        recorder.capture(input(150, 'rr'));
        recorder.capture(input(160, 'rc', 'right'));
        recorder.update(160, [[10, 16, 1]], 1, 'playing', 60);
        recorder.capture(input(170, 'rr'));
        recorder.capture(input(200, 'rc', 'right'));
        recorder.update(200, [[10, 11, 1]], 1, 'playing', 100);
        recorder.flag(0);
        recorder.capture(input(210, 'rr'));
        recorder.capture(input(250, 'lc'));
        recorder.capture(input(260, 'rc'));
        recorder.capture(input(300, 'lr', 'chord'));
        const replay = recorder.update(300, [[0, 11, 1]], 0, 'won', 200);
        recorder.completeQuestion(0);
        expect(replay?.chords).toEqual([{ flagMs: 100, leftMs: 150, chordMs: 200, eventIndex: 8 }]);
    });

    it('can select a particular event among observations with the same millisecond timestamp', () => {
        const recorder = new TrainingReplayRecorder([[16, 1, 10]], 1);
        recorder.capture(input(0, 'rc', 'right'));
        recorder.update(0, [[11, 1, 10]], 1, 'playing', 0);
        recorder.flag(0);
        recorder.capture(input(1, 'lc'));
        recorder.capture(input(1, 'lr', 'chord'));
        recorder.update(1, [[11, 1, 0]], 0, 'playing', 1);
        recorder.completeQuestion(0);
        recorder.capture(input(1, 'rr', null, 2));
        const replay = recorder.update(1, [[11, 1, 0]], 0, 'won', 1);
        if (replay === null) throw new Error('Missing replay');
        expect(replayFrame(replay, { timeMs: 1, eventIndex: replay.chords[0].eventIndex }).cursor?.columnIndex).toBe(0.5);
        expect(replayFrame(replay, { timeMs: 1 }).cursor?.columnIndex).toBe(2);
    });

    it('computes distance and click counts over a trailing one-second window, including partial movement segments', () => {
        const recorder = new TrainingReplayRecorder([[10]], 1);
        recorder.capture(input(0, 'lr', 'left'));
        recorder.update(0, [[0]], 1, 'playing', 0);
        recorder.capture(input(2000, 'mv', null, 4.5));
        const replay = recorder.update(2000, [[0]], 0, 'won', 2000);
        if (replay === null) throw new Error('Missing replay');
        const samples = replaySpeeds(replay);
        expect(samples.find((sample) => sample.timeMs === 500)).toEqual({ timeMs: 500, mouseSpeed: 1, clickSpeed: 1 });
        expect(samples.find((sample) => sample.timeMs === 1000)).toEqual({ timeMs: 1000, mouseSpeed: 2, clickSpeed: 0 });
        expect(samples.at(-1)).toEqual({ timeMs: 2000, mouseSpeed: 2, clickSpeed: 0 });
    });

    it('excludes the initial click, cancelled presses and chords from the click-duration histogram', () => {
        const recorder = new TrainingReplayRecorder([[10]], 1);
        recorder.capture(input(0, 'lr', 'left'));
        recorder.update(0, [[0]], 1, 'playing', 0);
        for (const event of [input(10, 'lc'), input(50, 'lr', 'left'), input(60, 'lc'), input(80, null), input(90, 'lr', 'left'), input(100, 'lc'), input(110, 'lr', 'chord'), input(120, 'lc'), input(150, 'lr', 'left')]) recorder.capture(event);
        const replay = recorder.update(150, [[0]], 0, 'won', 150);
        if (replay === null) throw new Error('Missing replay');
        expect(leftClickDurations(replay)).toEqual([40, 30]);
        const bins = clickDurationBins(replay);
        expect(bins.reduce((total, item) => total + item.length, 0)).toBe(2);
        expect(bins.map((item) => [item.x0, item.x1, item.length])).toEqual([
            [0, 10, 0], [10, 20, 0], [20, 30, 0], [30, 40, 1], [40, 50, 1],
        ]);
    });
});
