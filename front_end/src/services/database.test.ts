import 'fake-indexeddb/auto';

import { openDB } from 'idb';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import type { CacheRowSchema } from './database';

const CACHE_DB_NAME = 'saolei-cache';
const CACHE_DB_VERSION = 1;
const META_STORE_NAME = 'meta';
const USER_INFO_STORE_NAME = 'user-info';
const STORE_VERSIONS_KEY = 'storeVersions';
const ROW_SCHEMAS_KEY = 'rowSchemas';

// eslint-disable-next-line @typescript-eslint/consistent-type-imports
type DatabaseModule = typeof import('./database');

let activeDb: Awaited<ReturnType<DatabaseModule['getDatabase']>> | null = null;

function deleteDatabase(name: string) {
    return new Promise<void>((resolve, reject) => {
        const request = indexedDB.deleteDatabase(name);
        request.onsuccess = () => {
            resolve();
        };
        request.onerror = () => {
            reject(new Error(request.error?.message ?? `Deleting IndexedDB "${name}" failed`));
        };
        request.onblocked = () => {
            reject(new Error(`Deleting IndexedDB "${name}" was blocked`));
        };
    });
}

async function loadDatabaseModule() {
    vi.resetModules();
    return import('./database');
}

async function seedRawDatabase({
    row,
    storeVersions,
    rowSchemas,
}: {
    row?: Record<string, unknown>;
    storeVersions?: Record<string, number>;
    rowSchemas?: Record<string, CacheRowSchema>;
}) {
    const db = await openDB(CACHE_DB_NAME, CACHE_DB_VERSION, {
        upgrade(upgradeDb) {
            if (!upgradeDb.objectStoreNames.contains(META_STORE_NAME)) {
                upgradeDb.createObjectStore(META_STORE_NAME);
            }
            if (!upgradeDb.objectStoreNames.contains(USER_INFO_STORE_NAME)) {
                upgradeDb.createObjectStore(USER_INFO_STORE_NAME, { keyPath: 'id' });
            }
        },
    });

    if (storeVersions) {
        await db.put(META_STORE_NAME, storeVersions, STORE_VERSIONS_KEY);
    }
    if (rowSchemas) {
        await db.put(META_STORE_NAME, rowSchemas, ROW_SCHEMAS_KEY);
    }
    if (row) {
        await db.put(USER_INFO_STORE_NAME, row);
    }

    db.close();
}

async function openDatabase(module: DatabaseModule) {
    activeDb = await module.getDatabase();
    return activeDb;
}

async function seedCachedRow(
    module: DatabaseModule,
    row: Record<string, unknown>,
    rowSchema: CacheRowSchema,
) {
    const db = await openDatabase(module);
    await db.put(module.META_STORE_NAME, { [module.USER_INFO_STORE_NAME]: rowSchema }, ROW_SCHEMAS_KEY);
    await db.put(module.USER_INFO_STORE_NAME, row);
    return db;
}

describe('database service', () => {
    beforeEach(async () => {
        vi.restoreAllMocks();
        await deleteDatabase(CACHE_DB_NAME);
    });

    afterEach(() => {
        activeDb?.close();
        activeDb = null;
    });

    it('creates cache stores and writes store versions', async () => {
        const database = await loadDatabaseModule();
        const db = await openDatabase(database);

        expect(Array.from(db.objectStoreNames)).toEqual([
            database.META_STORE_NAME,
            database.USER_INFO_STORE_NAME,
        ]);
        expect(await db.get(database.META_STORE_NAME, STORE_VERSIONS_KEY)).toEqual(
            database.CACHE_STORE_SCHEMA_VERSIONS,
        );
    });

    it('clears a store when its fallback store version changes', async () => {
        await seedRawDatabase({
            row: { id: 1, name: 'stale cache' },
            storeVersions: { [USER_INFO_STORE_NAME]: 0 },
        });
        const database = await loadDatabaseModule();
        const db = await openDatabase(database);

        expect(await db.getAll(database.USER_INFO_STORE_NAME)).toEqual([]);
        expect(await db.get(database.META_STORE_NAME, STORE_VERSIONS_KEY)).toEqual(
            database.CACHE_STORE_SCHEMA_VERSIONS,
        );
    });

    it('migrates cached rows using registered row schema', async () => {
        const database = await loadDatabaseModule();
        await seedCachedRow(
            database,
            {
                id: '1',
                name: 'Alice',
                active: 'true',
                score: '123',
                tags: '["a","b"]',
                profile: '{"level":2}',
                obsolete: 'removed',
            },
            {
                id: { type: 'string' },
                name: { type: 'string' },
                active: { type: 'string' },
                score: { type: 'string' },
                tags: { type: 'string' },
                profile: { type: 'string' },
                obsolete: { type: 'string' },
            },
        );

        database.registerStoreRowSchema(database.USER_INFO_STORE_NAME, {
            id: { type: 'number' },
            name: { type: 'string' },
            active: { type: 'boolean' },
            score: { type: 'number' },
            tags: { type: 'array' },
            profile: { type: 'object' },
            count: { type: 'number', default: 0 },
        });
        const db = await openDatabase(database);

        expect(await db.get(database.USER_INFO_STORE_NAME, 1)).toEqual({
            id: 1,
            name: 'Alice',
            active: true,
            score: 123,
            tags: ['a', 'b'],
            profile: { level: 2 },
            count: 0,
        });
        expect(await db.get(database.META_STORE_NAME, ROW_SCHEMAS_KEY)).toEqual({
            [database.USER_INFO_STORE_NAME]: {
                id: { type: 'number' },
                name: { type: 'string' },
                active: { type: 'boolean' },
                score: { type: 'number' },
                tags: { type: 'array' },
                profile: { type: 'object' },
                count: { type: 'number', default: 0 },
            },
        });
    });

    it('clones object and array defaults during row migration', async () => {
        const database = await loadDatabaseModule();
        await seedCachedRow(
            database,
            { id: 1 },
            { id: { type: 'number' } },
        );
        const rowSchema = {
            id: { type: 'number' },
            settings: { type: 'object', default: { nested: true } },
            values: { type: 'array', default: [1, 2] },
        } satisfies CacheRowSchema;

        database.registerStoreRowSchema(database.USER_INFO_STORE_NAME, rowSchema);
        const db = await openDatabase(database);
        const row = await db.get(database.USER_INFO_STORE_NAME, 1) as {
            settings: { nested: boolean };
            values: number[];
        };
        row.settings.nested = false;
        row.values.push(3);

        expect(rowSchema.settings.default).toEqual({ nested: true });
        expect(rowSchema.values.default).toEqual([1, 2]);
    });

    it('clears a store when row migration fails', async () => {
        const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => undefined);
        const database = await loadDatabaseModule();
        await seedCachedRow(
            database,
            { id: 1, active: 'maybe' },
            {
                id: { type: 'number' },
                active: { type: 'string' },
            },
        );

        database.registerStoreRowSchema(database.USER_INFO_STORE_NAME, {
            id: { type: 'number' },
            active: { type: 'boolean' },
        });
        const db = await openDatabase(database);

        expect(await db.getAll(database.USER_INFO_STORE_NAME)).toEqual([]);
        expect(await db.get(database.META_STORE_NAME, ROW_SCHEMAS_KEY)).toEqual({
            [database.USER_INFO_STORE_NAME]: {
                id: { type: 'number' },
                active: { type: 'boolean' },
            },
        });
        expect(warnSpy).toHaveBeenCalledOnce();
        warnSpy.mockRestore();
    });

    it('reruns schema checks when a row schema is registered after an earlier getDatabase call', async () => {
        const database = await loadDatabaseModule();
        const db = await seedCachedRow(
            database,
            { id: '2', label: 'late registration' },
            {
                id: { type: 'string' },
                label: { type: 'string' },
            },
        );

        expect(await db.get(database.USER_INFO_STORE_NAME, '2')).toEqual({
            id: '2',
            label: 'late registration',
        });

        database.registerStoreRowSchema(database.USER_INFO_STORE_NAME, {
            id: { type: 'number' },
            label: { type: 'string' },
        });
        const latestDb = await openDatabase(database);

        expect(await latestDb.get(database.USER_INFO_STORE_NAME, 2)).toEqual({
            id: 2,
            label: 'late registration',
        });
        expect(await latestDb.get(database.USER_INFO_STORE_NAME, '2')).toBeUndefined();
    });

    it('provides public helpers for transactions and meta records', async () => {
        const database = await loadDatabaseModule();

        await database.setStoreMeta('customMeta', { enabled: true });
        expect(await database.getStoreMeta('customMeta')).toEqual({ enabled: true });

        const tx = await database.getTransaction(database.USER_INFO_STORE_NAME, 'readwrite');
        expect(tx.store).toBeDefined();
        await tx.store.put({ id: 7, label: 'written through transaction' });
        await tx.done;

        const db = await openDatabase(database);
        expect(await db.get(database.USER_INFO_STORE_NAME, 7)).toEqual({
            id: 7,
            label: 'written through transaction',
        });
    });

    it('deduplicates concurrent getDatabase calls while keeping row migration stable', async () => {
        const database = await loadDatabaseModule();
        await seedCachedRow(
            database,
            { id: '8', label: 'concurrent migration' },
            {
                id: { type: 'string' },
                label: { type: 'string' },
            },
        );
        database.registerStoreRowSchema(database.USER_INFO_STORE_NAME, {
            id: { type: 'number' },
            label: { type: 'string' },
        });

        const [db1, db2, db3] = await Promise.all([
            database.getDatabase(),
            database.getDatabase(),
            database.getDatabase(),
        ]);
        activeDb = db1;

        expect(db1).toBe(db2);
        expect(db2).toBe(db3);
        expect(await db1.get(database.USER_INFO_STORE_NAME, 8)).toEqual({
            id: 8,
            label: 'concurrent migration',
        });
    });
});
