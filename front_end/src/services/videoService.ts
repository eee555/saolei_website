import $axios from '@/http';
import { VideoAbstract } from '@/utils/videoabstract';
import type { VideoRedisInfo } from '@/utils/videoabstract';

type NewestQueueResponse = Record<string, string>;

export async function fetchNewestQueue(): Promise<VideoAbstract[]> {
    const { data } = await $axios.get<NewestQueueResponse>('/video/newest_queue/', {
        params: {},
    });

    return Object.entries(data).map(([key, rawVideoInfo]) => {
        const videoId = Number.parseInt(key, 10);
        const videoInfo = JSON.parse(rawVideoInfo) as VideoRedisInfo;
        return VideoAbstract.fromVideoRedisInfo(videoId, videoInfo);
    });
}
