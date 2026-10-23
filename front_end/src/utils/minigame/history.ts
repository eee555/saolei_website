import { openDB } from 'idb';
import type { DBSchema, IDBPDatabase } from 'idb';

import type { FlagChordMode } from './flagChordTraining';
import type { LeftClickMode } from './leftClickTraining';
import type { MissingCellMode, MissingCellRoundResult } from './missingCellTraining';
import type { TrainingReplay } from './replay';

export const MINIGAME_DB_NAME = 'saolei-minigame';
export const MINIGAME_DB_VERSION = 2;
export const MINIGAME_RESULTS_STORE = 'results';

/** Successful games only. This is local application data, not an export format. */
export type MinigameResult = { scoreMs: number } & (
    | { game: 'left-click'; mode: LeftClickMode; replay: TrainingReplay }
    | { game: 'flag-chord'; mode: FlagChordMode; replay: TrainingReplay }
    | { game: 'missing-cell'; mode: MissingCellMode; rounds: readonly MissingCellRoundResult[] }
);

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
        upgrade(db, oldVersion, newVersion, transaction) {
            if (oldVersion === 0) {
                const store = db.createObjectStore(MINIGAME_RESULTS_STORE, { keyPath: 'id', autoIncrement: true });
                store.createIndex('playedAt', 'playedAt');
                store.createIndex('scoreMs', 'scoreMs');
            } else if (oldVersion === 1 && newVersion === 2) {
                // Preserve beta history while renaming the old ranking identifier.
                void (async () => {
                    let cursor = await transaction.objectStore(MINIGAME_RESULTS_STORE).openCursor();
                    while (cursor !== null) {
                        const entry = cursor.value;
                        if (entry.game === 'left-click' && 'board' in entry.mode) {
                            const { board: rankingKey, ...mode } = entry.mode;
                            if (typeof rankingKey === 'string') await cursor.update({ ...entry, mode: { ...mode, rankingKey } });
                        }
                        cursor = await cursor.continue();
                    }
                })().catch(() => {
                    transaction.abort();
                });
            }
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
        const entry = structuredClone({ ...result, playedAt: Date.now() });
        const db = await getMinigameDatabase();
        return await db.add(MINIGAME_RESULTS_STORE, entry);
    } catch (error) {
        console.warn('Failed to save the minigame result to IndexedDB.', error);
        return undefined;
    }
}
