import { DBSchema, openDB } from 'idb';

import { serviceConfig } from './store';

import $axios from '@/http';
import { GetUserInfoResponse } from '@/utils/common/structInterface';
import { UserProfile } from '@/utils/userprofile';
import { VideoAbstract, VideoAbstractInfo } from '@/utils/videoabstract';

type UserInfoRow = GetUserInfoResponse;
type RequestStatus = 'pending' | 'inFlight';
type UserInfoRequest = {
    promise: Promise<GetUserInfoResponse>;
    resolve: (value: GetUserInfoResponse) => void;
    reject: (reason?: unknown) => void;
    status: RequestStatus;
    timeout: ReturnType<typeof setTimeout>;
};
interface UserInfoCacheDB extends DBSchema {
    'user-info': {
        key: number;
        value: UserInfoRow;
    };
}

const userInfoRequests = new Map<number, UserInfoRequest>();

const DB_NAME = 'saolei-user-info';
const DB_VERSION = 1;
const STORE_NAME = 'user-info';

const userInfoDB = openDB<UserInfoCacheDB>(DB_NAME, DB_VERSION, {
    upgrade(db) {
        if (!db.objectStoreNames.contains(STORE_NAME)) {
            db.createObjectStore(STORE_NAME, { keyPath: 'id' });
        }
    },
});

let poller: ReturnType<typeof setTimeout> | null = null;
let updateCachePromise: Promise<void> | null = null;

function scheduleFlushBufferIfNeeded() {
    if (poller) return;

    poller = setTimeout(() => {
        poller = null;
        void flushBuffer();
    }, serviceConfig.value.userInfoPollRate);
}

function enqueueRequest(userId: number): Promise<GetUserInfoResponse> {
    const existing = userInfoRequests.get(userId);
    if (existing) return existing.promise;

    let resolve!: (value: GetUserInfoResponse) => void;
    let reject!: (reason?: unknown) => void;
    const promise = new Promise<GetUserInfoResponse>((res, rej) => {
        resolve = res;
        reject = rej;
    });
    const timeout = setTimeout(() => {
        userInfoRequests.delete(userId);
        reject(new Error(`User ${userId} info request timed out`));
    }, Math.max(1, serviceConfig.value.userInfoRequestTimeout));

    const request = { promise, resolve, reject, status: 'pending' as const, timeout };
    userInfoRequests.set(userId, request);
    scheduleFlushBufferIfNeeded();

    return promise;
}

function shouldRefreshUpdatedUsers() {
    return Date.now() - serviceConfig.value.userInfoLastUpdate >= serviceConfig.value.userInfoUpdateInterval;
}

async function refreshUpdatedUsers() {
    if (!shouldRefreshUpdatedUsers()) return;
    if (updateCachePromise) return updateCachePromise;

    updateCachePromise = (async () => {
        const requestTime = Date.now();
        const { data } = await $axios.get('/api/userprofile/infoupdated', {
            params: { since: serviceConfig.value.userInfoLastUpdate },
        });
        const updatedUserIds = data as number[];
        const db = await userInfoDB;

        const tx = db.transaction(STORE_NAME, 'readwrite');
        await Promise.all(updatedUserIds.map((userId) => tx.store.delete(userId)));
        await tx.done;

        serviceConfig.value.userInfoLastUpdate = requestTime;
    })().finally(() => {
        updateCachePromise = null;
    });

    return updateCachePromise;
}

async function flushBuffer() {
    const pendingEntries = [...userInfoRequests.entries()].filter(([, request]) => request.status === 'pending');
    const entries = pendingEntries.slice(0, Math.max(1, serviceConfig.value.userInfoBulkSize));

    if (entries.length === 0) {
        if (userInfoRequests.size === 0 && poller) {
            clearTimeout(poller);
            poller = null;
        }
        return;
    }

    entries.forEach(([, request]) => request.status = 'inFlight');

    const userIds = entries.map(([id]) => id);
    try {
        const { data } = await $axios.get('/api/userprofile/infobulk', { params: { ids: userIds.join(',') } });
        const userInfos = data as GetUserInfoResponse[];
        const infoMap = new Map(userInfos.map((u) => [u.id, u]));
        const db = await userInfoDB;
        const tx = db.transaction(STORE_NAME, 'readwrite');

        await Promise.all(userInfos.map((userInfo) => tx.store.put(userInfo)));
        await tx.done;

        for (const [userId, { resolve, reject }] of entries) {
            const info = infoMap.get(userId);
            info ? resolve(info) : reject(new Error(`User ${userId} not returned by batch API`));
        }
    } catch (err) {
        entries.forEach(([, { reject }]) => reject(err));
    } finally {
        entries.forEach(([userId, request]) => {
            clearTimeout(request.timeout);
            if (userInfoRequests.get(userId) === request) {
                userInfoRequests.delete(userId);
            }
        });

        if ([...userInfoRequests.values()].some((request) => request.status === 'pending')) {
            scheduleFlushBufferIfNeeded();
        }
    }
}

export async function fetchUserInfo(userId: number) {
    try {
        await refreshUpdatedUsers().catch(() => undefined);
        const db = await userInfoDB;
        const cached = await db.get(STORE_NAME, userId);
        if (cached) return new UserProfile(cached);
    } catch {
        // 忽略 IndexedDB 错误（如隐私模式）
    }
    return new UserProfile(await enqueueRequest(userId));
}

export async function fetchUserIdentifiers(userId: number) {
    const response = await $axios.get('/api/userprofile/identifier', {
        params: { user_id: userId },
    });
    return response.data as string[];
}


const userVideosPendingRequests = new Map<number, Promise<VideoAbstract[]>>();
export function fetchUserVideos(userId: number) {
    const pendingRequest = userVideosPendingRequests.get(userId);

    if (pendingRequest) return pendingRequest;

    const promise = $axios.get('/api/userprofile/videolist', {
        params: { user_id: userId },
    }).then((response) => response.data.map((video: VideoAbstractInfo) => new VideoAbstract(video))).finally(() => {
        userVideosPendingRequests.delete(userId);
    });

    userVideosPendingRequests.set(userId, promise);
    return promise;
}
