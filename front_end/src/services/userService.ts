import $axios from '@/http';
import { GetUserInfoResponse } from '@/utils/common/structInterface';
import { VideoAbstract, VideoAbstractInfo } from '@/utils/videoabstract';

const userInfoCache = new Map<number, { promise: Promise<GetUserInfoResponse>; timestamp: number }>();
const userInfoCacheTTL = 5000 as const; // 5秒

export function fetchUserInfo(userId: number) {
    const now = Date.now();
    const cached = userInfoCache.get(userId);

    if (cached && now - cached.timestamp < userInfoCacheTTL) {
        return cached.promise;
    }

    const promise = $axios.get(`/api/userprofile/info/${userId}`).then((response) => {
        userInfoCache.set(userId, { promise, timestamp: now });
        return response.data as GetUserInfoResponse;
    }).catch((error) => {
        userInfoCache.delete(userId);
        throw error;
    });

    userInfoCache.set(userId, { promise, timestamp: now });
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
