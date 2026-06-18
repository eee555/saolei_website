import 'fake-indexeddb/auto';

import { openDB } from 'idb';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { GetUserInfoResponse } from '@/utils/common/structInterface';

const DB_NAME = 'saolei-user-info';
const DB_VERSION = 1;
const STORE_NAME = 'user-info';

type ServiceConfigValue = {
    userInfoUpdateInterval: number;
    userInfoLastUpdate: number;
    userInfoBatchDelay: number;
    userInfoBatchSize: number;
};

const axiosGet = vi.fn();
const serviceConfig = {
    value: {
        userInfoUpdateInterval: 86400000,
        userInfoLastUpdate: Date.now(),
        userInfoBatchDelay: 1,
        userInfoBatchSize: 100,
    } as ServiceConfigValue,
};

vi.mock('@/http', () => ({ default: { get: axiosGet } }));
vi.mock('./store', () => ({ serviceConfig }));

function createUser(id: number, realname: string): GetUserInfoResponse {
    return {
        id, username: `user${id}`,
        firstname: '', lastname: '', realname,
        is_banned: false, is_staff: false,
        country: '', signature: '',
        last_change_avatar: '', last_change_signature: '',
        left_avatar_n: 0, left_signature_n: 0,
    };
}

async function openUserInfoDB() {
    return openDB(DB_NAME, DB_VERSION, {
        upgrade(db) {
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                db.createObjectStore(STORE_NAME, { keyPath: 'id' });
            }
        },
    });
}

async function putCachedUser(user: GetUserInfoResponse) {
    const db = await openUserInfoDB();
    await db.put(STORE_NAME, user);
    db.close();
}

async function getCachedUser(userId: number) {
    const db = await openUserInfoDB();
    const user = await db.get(STORE_NAME, userId);
    db.close();
    return user as GetUserInfoResponse | undefined;
}

async function loadFetchUserInfo(config: Partial<ServiceConfigValue> = {}) {
    vi.resetModules();
    Object.assign(serviceConfig.value, {
        userInfoUpdateInterval: 86400000,
        userInfoLastUpdate: Date.now(),
        userInfoBatchDelay: 1,
        userInfoBatchSize: 100,
        ...config,
    });

    const { fetchUserInfo } = await import('./userService');
    return fetchUserInfo;
}

async function clearUserInfoDB() {
    const db = await openUserInfoDB();
    await db.clear(STORE_NAME);
    db.close();
}

async function waitForBatch() {
    await new Promise((resolve) => setTimeout(resolve, serviceConfig.value.userInfoBatchDelay + 10));
}

describe('fetchUserInfo', () => {
    beforeEach(async () => {
        axiosGet.mockReset();
        await clearUserInfoDB();
    });

    it('returns cached user info without requesting infobulk', async () => {
        await putCachedUser(createUser(1, 'Cached User'));
        const fetchUserInfo = await loadFetchUserInfo();

        const user = await fetchUserInfo(1);

        expect(user.id).toBe(1);
        expect(user.realname).toBe('Cached User');
        expect(axiosGet).not.toHaveBeenCalled();
    });

    it('clears local cache instead of requesting infoupdated when lastUpdate is zero', async () => {
        await putCachedUser(createUser(1, 'Stale User'));
        const fetchUserInfo = await loadFetchUserInfo({
            userInfoLastUpdate: 0,
            userInfoUpdateInterval: 0,
        });
        axiosGet.mockResolvedValueOnce({ data: [createUser(1, 'Fresh User')] });

        const promise = fetchUserInfo(1);
        await waitForBatch();
        const user = await promise;

        expect(user.realname).toBe('Fresh User');
        expect((await getCachedUser(1))?.realname).toBe('Fresh User');
        expect(axiosGet).toHaveBeenCalledTimes(1);
        expect(axiosGet).toHaveBeenCalledWith('/api/userprofile/infobulk', { params: { ids: '1' } });
    });

    it('deletes updated cached users before reading from IndexedDB', async () => {
        await putCachedUser(createUser(1, 'Stale User'));
        const fetchUserInfo = await loadFetchUserInfo({
            userInfoLastUpdate: 100,
            userInfoUpdateInterval: 0,
        });
        axiosGet.mockImplementationOnce(async () => ({ data: [1] }));
        axiosGet.mockImplementationOnce(async () => ({ data: [createUser(1, 'Fresh User')] }));

        const promise = fetchUserInfo(1);
        await waitForBatch();
        const user = await promise;

        expect(user.realname).toBe('Fresh User');
        expect(axiosGet).toHaveBeenNthCalledWith(1, '/api/userprofile/infoupdated', { params: { since: 100 } });
        expect(axiosGet).toHaveBeenNthCalledWith(2, '/api/userprofile/infobulk', { params: { ids: '1' } });
    });

    it('batches concurrent cache misses into one infobulk request', async () => {
        const fetchUserInfo = await loadFetchUserInfo();
        axiosGet.mockResolvedValueOnce({
            data: [
                createUser(1, 'User One'),
                createUser(2, 'User Two'),
            ],
        });

        const user1Promise = fetchUserInfo(1);
        const user2Promise = fetchUserInfo(2);
        await waitForBatch();
        const [user1, user2] = await Promise.all([user1Promise, user2Promise]);

        expect(user1.realname).toBe('User One');
        expect(user2.realname).toBe('User Two');
        expect(axiosGet).toHaveBeenCalledTimes(1);
        expect(axiosGet).toHaveBeenCalledWith('/api/userprofile/infobulk', { params: { ids: '1,2' } });
    });
});
