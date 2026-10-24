import { openDB } from 'idb';
import type { DBSchema, IDBPDatabase } from 'idb';

import type { FlagChordMode } from './flagChordTraining';
import type { LeftClickMode } from './leftClickTraining';
import type { MissingCellMode, MissingCellRoundResult } from './missingCellTraining';
import type { TrainingRecording } from './replay';

export const MINIGAME_DB_NAME = 'saolei-minigame';
export const MINIGAME_DB_VERSION = 1;
export const MINIGAME_RESULTS_STORE = 'results';

/** Successful games only. This is local application data, not an export format. */
export type MinigameResult = { scoreMs: number } & (
    | { game: 'left-click'; mode: LeftClickMode; replay: TrainingRecording }
    | { game: 'flag-chord'; mode: FlagChordMode; replay: TrainingRecording }
    | { game: 'missing-cell'; mode: MissingCellMode; rounds: readonly MissingCellRoundResult[] }
);

export type MinigameReplayData = TrainingRecording | { rounds: readonly MissingCellRoundResult[] };

export type MinigameHistoryEntry = MinigameResult & {
    id?: number;

    /** Completion time as Unix milliseconds; independent of the monotonic game clock. */
    playedAt: number;
};

export interface MinigameHistoryDB extends DBSchema {
    [MINIGAME_RESULTS_STORE]: {
        key: number;
        value: MinigameHistoryEntry;
        indexes: { playedAt: number; scoreMs: number };
    };
}

let databasePromise: Promise<IDBPDatabase<MinigameHistoryDB>> | undefined;

/** Kept separate from disposable website caches so cache upgrades never clear game history. */
export function getMinigameDatabase(): Promise<IDBPDatabase<MinigameHistoryDB>> {
    if (databasePromise !== undefined) return databasePromise;
    const opening: Promise<IDBPDatabase<MinigameHistoryDB>> = openDB<MinigameHistoryDB>(MINIGAME_DB_NAME, MINIGAME_DB_VERSION, {
        upgrade(db) {
            const store = db.createObjectStore(MINIGAME_RESULTS_STORE, { keyPath: 'id', autoIncrement: true });
            store.createIndex('playedAt', 'playedAt');
            store.createIndex('scoreMs', 'scoreMs');
        },
        blocking() {
            void opening.then((db) => {
                db.close();
            });
            if (databasePromise === opening) databasePromise = undefined;
        },
        terminated() {
            if (databasePromise === opening) databasePromise = undefined;
        },
    });
    databasePromise = opening;
    void opening.catch(() => {
        if (databasePromise === opening) databasePromise = undefined;
    });
    return opening;
}

/** Snapshot immediately, before awaiting IndexedDB, so restarting cannot change the pending save. */
export async function saveMinigameResult(result: MinigameResult): Promise<number | undefined> {
    try {
        const data = result.game === 'missing-cell' ? result : { ...result, replay: { initialBoard: result.replay.initialBoard, events: result.replay.events } };
        const entry = structuredClone({ ...data, playedAt: Date.now() });
        const db = await getMinigameDatabase();
        return await db.add(MINIGAME_RESULTS_STORE, entry);
    } catch (error) {
        console.warn('Failed to save the minigame result to IndexedDB.', error);
        return undefined;
    }
}
