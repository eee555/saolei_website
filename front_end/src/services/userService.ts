import $axios from '@/http';
import { GetUserInfoResponse } from '@/utils/common/structInterface';
import { VideoAbstract, VideoAbstractInfo } from '@/utils/videoabstract';

export async function fetchUserInfo(userId: number) {
    const response = await $axios.get('/api/userprofile/info', {
        params: { user_id: userId },
    });
    return response.data as GetUserInfoResponse;
}

export async function fetchUserIdentifiers(userId: number) {
    const response = await $axios.get('/api/userprofile/identifier', {
        params: { user_id: userId },
    });
    return response.data as string[];
}

export async function fetchUserVideos(userId: number) {
    const response = await $axios.get('/api/userprofile/videolist', {
        params: { user_id: userId },
    });
    return response.data.map((video: VideoAbstractInfo) => new VideoAbstract(video));
}
