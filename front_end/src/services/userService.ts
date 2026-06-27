import type { CacheRowSchema } from './database';
import { getDatabase, getTransaction, registerStoreRowSchema, USER_INFO_STORE_NAME } from './database';
import { serviceConfig } from './store';

import $axios from '@/http';
import type { GetUserInfoResponse } from '@/utils/common/structInterface';
import { UserProfile } from '@/utils/userprofile';
import type { VideoAbstractInfo } from '@/utils/videoabstract';
import { VideoAbstract } from '@/utils/videoabstract';

type RequestStatus = 'pending' | 'inFlight';
interface UserInfoRequest {
    promise: Promise<GetUserInfoResponse>;
    resolve: (value: GetUserInfoResponse) => void;
    reject: (reason?: unknown) => void;
    status: RequestStatus;
}

const userInfoRequests = new Map<number, UserInfoRequest>();

registerStoreRowSchema(USER_INFO_STORE_NAME, {
    id: { type: 'number' },
    username: { type: 'string', default: '' },
    firstname: { type: 'string', default: '' },
    lastname: { type: 'string', default: '' },
    realname: { type: 'string', default: '' },
    is_banned: { type: 'boolean', default: false },
    is_staff: { type: 'boolean', default: false },
    country: { type: 'string', default: '' },
    signature: { type: 'string', default: '' },
    last_change_avatar: { type: 'string', default: '' },
    last_change_signature: { type: 'string', default: '' },
    left_avatar_n: { type: 'number', default: 0 },
    left_signature_n: { type: 'number', default: 0 },
} satisfies CacheRowSchema);

let batchTimer: ReturnType<typeof setTimeout> | null = null;
let updateCachePromise: Promise<void> | null = null;

function scheduleBatchIfNeeded() {
    if (batchTimer) return;

    batchTimer = setTimeout(() => {
        batchTimer = null;
        void processUserInfoBatch();
    }, serviceConfig.value.userInfoBatchDelay);
}

/**
 * 将用户信息请求加入队列，如果同一用户已有请求则返回现有请求的Promise
 * @param userId 用户ID
 * @returns 返回一个Promise，解析为GetUserInfoResponse类型的结果
 */
function enqueueRequest(userId: number): Promise<GetUserInfoResponse> {
    // 检查是否已有该用户的请求。如果存在，直接返回现有请求的Promise
    const existing = userInfoRequests.get(userId);
    if (existing) return existing.promise;

    // 定义Promise的resolve和reject函数，创建一个新的Promise
    const { promise, resolve, reject } = Promise.withResolvers<GetUserInfoResponse>();

    const request = { promise, resolve, reject, status: 'pending' as const };
    userInfoRequests.set(userId, request);
    scheduleBatchIfNeeded();

    return promise;
}

function shouldRefreshUpdatedUsers() {
    return Date.now() - serviceConfig.value.userInfoLastUpdate >= serviceConfig.value.userInfoUpdateInterval;
}

/**
 * 刷新已更新用户信息的异步函数
 * 该函数会检查是否需要刷新用户信息，并更新本地缓存
 * 使用IndexedDB存储用户信息，并通过API获取更新后的用户数据
 */
async function refreshUpdatedUsers() {
    if (!shouldRefreshUpdatedUsers()) return;
    if (updateCachePromise) return updateCachePromise;

    // 创建并执行刷新缓存的操作
    updateCachePromise = (async () => {
        // 初始化
        const requestTime = Date.now();
        const lastUpdate = serviceConfig.value.userInfoLastUpdate;
        const tx = await getTransaction(USER_INFO_STORE_NAME, 'readwrite');
        const { store } = tx;

        // 如果是首次更新（lastUpdate为0），则清空整个存储
        if (lastUpdate === 0) {
            await store.clear();
            await tx.done;

            serviceConfig.value.userInfoLastUpdate = requestTime;
            return;
        }

        // 获取自上次更新以来有更新的用户ID列表，删除所有已更新的用户记录
        const { data } = await $axios.get('/api/userprofile/infoupdated', {
            params: { since: lastUpdate },
        });
        const updatedUserIds = data as number[];
        await Promise.all(updatedUserIds.map((userId) => store.delete(userId)));
        await tx.done;

        serviceConfig.value.userInfoLastUpdate = requestTime;
    })().finally(() => {
        // 操作完成后清除Promise引用
        updateCachePromise = null;
    });

    return updateCachePromise;
}

/**
 * 批量处理待处理的用户信息请求
 * 该函数会从请求队列中获取指定数量的待处理请求，并发送批量请求获取用户信息
 * 然后将结果存储到数据库并解决相应的Promise
 */
async function processUserInfoBatch() {
    // 获取所有状态为'pending'的请求，并转换为数组
    const pendingEntries = [...userInfoRequests.entries()].filter(([, request]) => request.status === 'pending');
    // 根据配置的批量大小获取要处理的请求数量，至少为1
    const entries = pendingEntries.slice(0, Math.max(1, serviceConfig.value.userInfoBatchSize));

    // 如果没有待处理条目
    if (entries.length === 0) {
        // 如果没有待处理的请求且存在批处理定时器，则清除定时器
        if (userInfoRequests.size === 0 && batchTimer) {
            clearTimeout(batchTimer);
            batchTimer = null;
        }
        return; // 直接返回，不执行任何操作
    }

    // 将所有选中的请求状态设置为'inFlight'（正在处理）
    entries.forEach(([, request]) => {
        request.status = 'inFlight';
    });

    // 提取用户ID数组，用于批量请求
    const userIds = entries.map(([id]) => id);
    try {
        // 发送批量请求获取用户信息
        const { data } = await $axios.get('/api/userprofile/infobulk', { params: { ids: userIds.join(',') } });
        const userInfos = data as GetUserInfoResponse[];

        // 将所有用户信息存储到数据库
        const infoMap = new Map(userInfos.map((u) => [u.id, u]));
        const tx = await getTransaction(USER_INFO_STORE_NAME, 'readwrite');
        const { store } = tx;

        await Promise.all(userInfos.map((userInfo) => store.put(userInfo)));
        await tx.done;

        // 遍历所有请求，解决或拒绝相应的Promise
        for (const [userId, { resolve, reject }] of entries) {
            const info = infoMap.get(userId);
            // 如果找到用户信息，则解决Promise；否则拒绝
            if (info) resolve(info);
            else reject(new Error(`User ${userId} not returned by batch API`));
        }
    } catch (err) {
        // 如果发生错误，拒绝所有请求
        entries.forEach(([, { reject }]) => {
            reject(err);
        });
    } finally {
        // 清理已处理的请求
        entries.forEach(([userId]) => {
            userInfoRequests.delete(userId);
        });

        // 如果还有待处理的请求，检查是否需要安排刷新缓冲区
        if ([...userInfoRequests.values()].some((request) => request.status === 'pending')) {
            scheduleBatchIfNeeded();
        }
    }
}

export async function fetchUserInfo(userId: number): Promise<UserProfile> {
    try {
        await refreshUpdatedUsers().catch(() => undefined);
        const db = await getDatabase();
        const cached = await db.get(USER_INFO_STORE_NAME, userId) as GetUserInfoResponse | undefined;
        if (cached) return new UserProfile(cached);
    } catch {
        // 忽略 IndexedDB 错误（如隐私模式）
    }
    return new UserProfile(await enqueueRequest(userId));
}

export async function fetchUserIdentifiers(userId: number): Promise<string[]> {
    const response = await $axios.get('/api/userprofile/identifier', {
        params: { user_id: userId },
    });
    return response.data as string[];
}

const userVideosPendingRequests = new Map<number, Promise<VideoAbstract[]>>();
export function fetchUserVideos(userId: number): Promise<VideoAbstract[]> {
    const pendingRequest = userVideosPendingRequests.get(userId);

    if (pendingRequest) return pendingRequest;

    const promise = $axios.get('/api/userprofile/videolist', {
        params: { user_id: userId },
    }).then(({ data }) => (data as VideoAbstractInfo[]).map((video) => new VideoAbstract(video))).finally(() => {
        userVideosPendingRequests.delete(userId);
    });

    userVideosPendingRequests.set(userId, promise);
    return promise;
}
