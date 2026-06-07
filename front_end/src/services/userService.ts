import $axios from '@/http';
import { localDatabase } from '@/services/localDatabase';
import type { LocalUser } from '@/services/localDatabase';
import { sleep } from '@/utils';
import { GetUserInfoResponse } from '@/utils/common/structInterface';
import { VideoAbstract, VideoAbstractInfo } from '@/utils/videoabstract';

const userInfoPendingRequests = new Map<number, Promise<GetUserInfoResponse>>();
const userInfoRequestInterval = 100 as const; // 10 requests per second
const userInfoRateLimitPause = 60000 as const; // 1 minute
const userInfoCacheTTL = 86400000 as const; // 1 day
let lastUserInfoRequestTime = 0;
let userInfoRequestQueue = Promise.resolve();

async function getCachedUserInfo(userId: number, now: number) {
    const cached = await localDatabase.users.get(userId);
    if (!cached) {
        return null;
    }

    if (now - cached.updatedAt >= userInfoCacheTTL) {
        await localDatabase.users.delete(userId);
        return null;
    }

    return localUserToUserInfo(cached);
}

function userInfoToLocalUser(userId: number, data: GetUserInfoResponse): LocalUser {
    return {
        id: data.id ?? userId,
        username: data.username,
        realname: data.realname,
        firstname: data.firstname,
        lastname: data.lastname,
        is_banned: data.is_banned,
        is_staff: data.is_staff,
        country: data.country,
        signature: data.signature,
        last_change_avatar: data.last_change_avatar,
        last_change_signature: data.last_change_signature,
        left_avatar_n: data.left_avatar_n,
        left_signature_n: data.left_signature_n,
        updatedAt: Date.now(),
    };
}

function localUserToUserInfo(user: LocalUser): GetUserInfoResponse {
    return {
        id: user.id,
        username: user.username,
        realname: user.realname,
        firstname: user.firstname,
        lastname: user.lastname,
        is_banned: user.is_banned,
        is_staff: user.is_staff,
        country: user.country,
        signature: user.signature,
        last_change_avatar: user.last_change_avatar,
        last_change_signature: user.last_change_signature,
        left_avatar_n: user.left_avatar_n,
        left_signature_n: user.left_signature_n,
    };
}

function scheduleUserInfoRequest(userId: number) {
    const runRequest = userInfoRequestQueue.then(async () => {
        while (true) {
            const delay = Math.max(0, lastUserInfoRequestTime + userInfoRequestInterval - Date.now());

            if (delay > 0) {
                await sleep(delay);
            }

            lastUserInfoRequestTime = Date.now();

            try {
                const response = await $axios.get(`/api/userprofile/info/${userId}`);
                return response.data as GetUserInfoResponse;
            } catch (error: any) {
                if (error.response.status !== 429) throw error;
                await sleep(userInfoRateLimitPause);
            }
        }
    });

    userInfoRequestQueue = runRequest.then(
        () => undefined,
        () => undefined,
    );

    return runRequest;
}

export async function fetchUserInfo(userId: number) {
    const now = Date.now();
    const cached = await getCachedUserInfo(userId, now);

    if (cached) return cached;

    const pendingRequest = userInfoPendingRequests.get(userId);
    if (pendingRequest) return pendingRequest;

    const promise = scheduleUserInfoRequest(userId).then(async (data) => {
        await localDatabase.users.put(userInfoToLocalUser(userId, data));
        userInfoPendingRequests.delete(userId);
        return data;
    }).catch((error) => {
        userInfoPendingRequests.delete(userId);
        throw error;
    });

    userInfoPendingRequests.set(userId, promise);
    return promise;
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
