import $axios from '@/http';
import { AccountLinks } from '@/utils/accountlinks';
import type { AccountLinkPlatform, AccountLinkQueueResponse, AccountLinksResponse, SaoleiVideo, SaoleiVideoRaw } from '@/utils/accountlinks';

export async function fetchAccountLinks(userId: number): Promise<AccountLinks> {
    const { data } = await $axios.get<AccountLinksResponse>(`/api/accountlink/${userId}`);
    return new AccountLinks(data);
}

export async function addAccountLink(platform: AccountLinkPlatform, identifier: string): Promise<AccountLinkQueueResponse> {
    const { data } = await $axios.post<AccountLinkQueueResponse>('/api/accountlink/create/', {
        platform,
        identifier,
    });
    return data;
}

export async function fetchSaoleiImportVideos(saoleiId: number): Promise<SaoleiVideo[]> {
    const { data } = await $axios.get<SaoleiVideoRaw[]>('accountlink/saolei/videolist/get/', {
        params: { saolei_id: saoleiId },
    });
    return data.map(normalizeSaoleiVideo);
}

function normalizeSaoleiVideo(video: SaoleiVideoRaw): SaoleiVideo {
    return {
        ...video,
        import_video__id: video.import_video__id ?? 0,
        import_task__status: video.import_task__status ?? 'NULL',
    };
}
