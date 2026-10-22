import { fetchVideoInfos, videoDisplayFields } from './videoInfoService';
import type { VideoMetadata } from './videoInfoService';

import $axios from '@/http';
import { VideoAbstract } from '@/utils/videoabstract';

export async function fetchVideoList(url: string, params: Record<string, unknown> = {}): Promise<VideoAbstract[]> {
    const { data } = await $axios.get<VideoMetadata[]>(url, { params });
    return (await fetchVideoInfos(data)).map((row) => new VideoAbstract({ ...videoDisplayFields(row), ...row, bv: row.bv ?? NaN }));
}

export async function fetchNewestQueue(): Promise<VideoAbstract[]> {
    return fetchVideoList('/api/video/newest_queue');
}
