import $axios from '@/http';
import { AccountLinks } from '@/utils/accountlinks';
import type { AccountLinkPlatform, AccountLinkQueueResponse, AccountLinksResponse, SaoleiVideo, SaoleiVideoRaw } from '@/utils/accountlinks';

type AccountLinkUpdateErrorMessageCategory = 'cooldown' | 'empty' | 'indexerror' | 'pageempty' | 'requestexception' | 'timeout' | 'unknown';

const accountLinkUpdateErrorCategories = new Set<string>([
    'cooldown',
    'empty',
    'indexerror',
    'pageempty',
    'requestexception',
    'timeout',
]);

interface AccountLinkUpdateSuccessResponse {
    type: 'success';
}

interface AccountLinkUpdateErrorResponse {
    type: 'error';
    object?: string;
    category?: string;
}

export type AccountLinkUpdateResponse = AccountLinkUpdateSuccessResponse | AccountLinkUpdateErrorResponse;

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

export async function updateAccountLink(platform: AccountLinkPlatform): Promise<AccountLinkUpdateResponse> {
    const { data } = await $axios.post<AccountLinkUpdateResponse>('accountlink/update/', {
        platform,
    });
    return data;
}

export function getAccountLinkUpdateErrorMessageKey(category?: string): string {
    return `accountlink.updateError.${getAccountLinkUpdateErrorMessageCategory(category)}`;
}

function getAccountLinkUpdateErrorMessageCategory(category?: string): AccountLinkUpdateErrorMessageCategory {
    if (category !== undefined && accountLinkUpdateErrorCategories.has(category)) {
        return category as AccountLinkUpdateErrorMessageCategory;
    }
    return 'unknown';
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
