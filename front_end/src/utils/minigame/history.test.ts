import 'fake-indexeddb/auto';

import { deleteDB, openDB } from 'idb';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { flagChordModes, FlagChordTraining } from './flagChordTraining';
import type { MinigameResult } from './history';
import { leftClickModes, LeftClickTraining } from './leftClickTraining';
import { missingCellModes, MissingCellTraining, reviewMissingCellRound } from './missingCellTraining';
import { missingCellCandidates } from './missingCellTraining.testHelpers';
import { rebuildTrainingReplay, replayFrame, TrainingReplayRecorder } from './replay';
import type { TrainingMouseInput, TrainingReplay } from './replay';

const databaseName = 'saolei-minigame';

function input(now: number, row: number, column: number, action: TrainingMouseInput['action'], trigger: TrainingMouseInput['trigger']): TrainingMouseInput {
    return { now, row: row + 0.5, column: column + 0.5, action, trigger, state: action === 'rc' ? 'ud' : action === 'lc' ? 'dd' : 'uu', pressed: null };
}

function leftClickResult(): Extract<MinigameResult, { game: 'left-click' }> {
    const game = new LeftClickTraining(leftClickModes[2], () => 0.37);
    const recorder = new TrainingReplayRecorder('left-click', game.board);
    const safe = game.board.flatMap((row, r) => row.flatMap((value, c) => (value === 10 ? [{ row: r, column: c }] : [])));
    let replay: TrainingReplay | null = null;
    for (const [index, { row, column }] of safe.entries()) {
        const now = 100 + index * 50;
        recorder.capture(input(now - 10, row, column, 'lc', null));
        recorder.capture(input(now, row, column, 'lr', 'left'));
        game.trigger(row, column, now);
        replay = recorder.update(now, game.phase, game.elapsedMs(now));
    }
    if (replay === null) throw new Error('Missing completed left-click replay');
    return { game: 'left-click', mode: game.mode, scoreMs: game.elapsedMs(99999), replay: { initialBoard: replay.initialBoard, events: replay.events } };
}

function flagChordResult(): Extract<MinigameResult, { game: 'flag-chord' }> {
    const game = new FlagChordTraining(flagChordModes[0], () => 0.37);
    const recorder = new TrainingReplayRecorder('flag-chord', game.board);
    let replay: TrainingReplay | null = null;
    for (const [index, question] of game.questions.entries()) {
        const now = 100 + index * 100;
        const row = Math.floor(question.mine / game.mode.columns);
        const column = question.mine % game.mode.columns;
        recorder.capture(input(now, row, column, 'rc', 'right'));
        game.act('right', row, column, now);
        recorder.update(now, game.phase, game.elapsedMs(now));
        recorder.capture(input(now + 20, question.row, question.column, 'lc', null));
        recorder.capture(input(now + 40, question.row, question.column, 'lr', 'chord'));
        game.act('chord', question.row, question.column, now + 40);
        replay = recorder.update(now + 40, game.phase, game.elapsedMs(now + 40));
    }
    if (replay === null) throw new Error('Missing completed flag-and-chord replay');
    return { game: 'flag-chord', mode: game.mode, scoreMs: game.elapsedMs(99999), replay: { initialBoard: replay.initialBoard, events: replay.events } };
}

function missingCellResult(): Extract<MinigameResult, { game: 'missing-cell' }> {
    let draw = 0;
    const game = new MissingCellTraining(missingCellModes[0], () => (++draw * 0.61803398875) % 1);
    game.trigger(0, 0, 1000);
    for (let round = 0; round < 10; round++) {
        const [target] = missingCellCandidates(game.board);
        game.trigger(target.row, target.column, 1100 + round * 100);
    }
    return { game: 'missing-cell', mode: game.mode, scoreMs: game.elapsedMs(99999), rounds: game.roundResults };
}

describe('local minigame history', () => {
    beforeEach(async () => {
        vi.resetModules();
        await deleteDB(databaseName);
    });
    afterEach(async () => {
        vi.unstubAllGlobals();
        vi.restoreAllMocks();
        await deleteDB(databaseName);
    });

    it('persists all three successful games without overwriting equal times or scores and reopens their review data', async () => {
        vi.spyOn(Date, 'now').mockReturnValue(123456789);
        const history = await import('./history');
        const results = [leftClickResult(), flagChordResult(), missingCellResult(), leftClickResult()];
        const ids = await Promise.all(results.map((result) => history.saveMinigameResult(result)));
        expect(new Set(ids).size).toBe(results.length);
        expect(ids.every((id) => typeof id === 'number')).toBe(true);

        vi.resetModules();
        const reloaded = await import('./history');
        const db = await reloaded.getMinigameDatabase();
        const entries = await db.getAll(reloaded.MINIGAME_RESULTS_STORE);
        expect(entries).toEqual(results.map((result, index) => ({ ...result, id: ids[index], playedAt: 123456789 })));
        for (const entry of entries) {
            if (entry.game === 'missing-cell') {
                expect(entry.rounds).toHaveLength(10);
                expect(entry.rounds.reduce((total, round) => total + round.timeMs, 0)).toBe(entry.scoreMs);
                for (const round of entry.rounds) {
                    expect(Object.keys(round).sort()).toEqual(['board', 'timeMs']);
                    const preview = reviewMissingCellRound(round);
                    expect(preview.target).toEqual(missingCellCandidates(preview.board)[0]);
                }
            } else {
                expect(Object.keys(entry.replay).sort()).toEqual(['events', 'initialBoard']);
                const replay = rebuildTrainingReplay(entry.game, entry.replay, entry.scoreMs);
                expect(replayFrame(replay, { timeMs: entry.scoreMs }).remaining).toBe(0);
                expect(replayFrame(replay, { timeMs: 0 }).cursor).toBeDefined();
                if (entry.game === 'flag-chord') expect(replay.chords).toHaveLength(4);
            }
        }
        db.close();
    });

    it('omits expanded snapshots, counters and chord timings from persisted replay data', async () => {
        const history = await import('./history');
        const result = flagChordResult();
        const replay = rebuildTrainingReplay(result.game, result.replay, result.scoreMs);
        expect(replay.chords).toHaveLength(4);
        const id = await history.saveMinigameResult({ ...result, replay });
        if (id === undefined) throw new Error('Missing saved game');
        const db = await history.getMinigameDatabase();
        const saved = await db.get(history.MINIGAME_RESULTS_STORE, id);
        if (saved?.game !== 'flag-chord') throw new Error('Wrong saved game');
        expect(saved.replay).toEqual(result.replay);
        expect(Object.keys(saved.replay).sort()).toEqual(['events', 'initialBoard']);
    });

    it('indexes completion time and numeric score independently', async () => {
        const history = await import('./history');
        const timestamp = vi.spyOn(Date, 'now');
        for (const [result, playedAt] of [[leftClickResult(), 100], [flagChordResult(), 300], [missingCellResult(), 200]] as const) {
            timestamp.mockReturnValue(playedAt);
            await history.saveMinigameResult(result);
        }
        const db = await history.getMinigameDatabase();
        expect(Array.from(db.transaction(history.MINIGAME_RESULTS_STORE).store.indexNames)).toEqual(['playedAt', 'scoreMs']);
        expect((await db.getAllFromIndex(history.MINIGAME_RESULTS_STORE, 'playedAt')).map((entry) => entry.game)).toEqual(['left-click', 'missing-cell', 'flag-chord']);
        expect((await db.getAllFromIndex(history.MINIGAME_RESULTS_STORE, 'scoreMs')).map((entry) => entry.game)).toEqual(['flag-chord', 'left-click', 'missing-cell']);
    });

    it('snapshots data before the first database await so a restart cannot alter a pending save', async () => {
        const history = await import('./history');
        const result = leftClickResult();
        const original = structuredClone(result);
        const pending = history.saveMinigameResult(result);
        result.replay.events.length = 0;
        result.replay.initialBoard[0][0] = 99;
        result.scoreMs = 1;
        const id = await pending;
        if (id === undefined) throw new Error('Missing saved game');
        const db = await history.getMinigameDatabase();
        expect(await db.get(history.MINIGAME_RESULTS_STORE, id)).toMatchObject(original);
    });

    it('imports without IndexedDB, handles storage failure, and retries the next result', async () => {
        vi.stubGlobal('indexedDB', undefined);
        const warning = vi.spyOn(console, 'warn').mockImplementation(() => undefined);
        const history = await import('./history');
        expect(await history.saveMinigameResult(leftClickResult())).toBeUndefined();
        expect(warning).toHaveBeenCalledOnce();
        vi.unstubAllGlobals();
        expect(await history.saveMinigameResult(leftClickResult())).toBeTypeOf('number');
    });

    it('releases old connections for an upgrade without clearing saved games', async () => {
        const history = await import('./history');
        await history.saveMinigameResult(leftClickResult());
        const upgraded = await openDB(databaseName, history.MINIGAME_DB_VERSION + 1);
        expect(await upgraded.count(history.MINIGAME_RESULTS_STORE)).toBe(1);
        upgraded.close();
    });
});
