import { isAxiosError } from 'axios';

import $axios from '@/http';
import { AccountLinks, MineracerAccountLinkSession } from '@/utils/accountlinks';
import type { AccountLinkPlatform, AccountLinkQueueResponse, AccountLinksResponse, MineracerAccountLinkSessionResponse, SaoleiVideo, SaoleiVideoRaw } from '@/utils/accountlinks';

type MineracerAccountLinkErrorMessageCategory = 'account_not_found' | 'already_linked' | 'expired' | 'identifier_conflict' | 'invalid_device_code' | 'invalid_userid' | 'link_superseded' | 'not_configured' | 'pending_start' | 'remote_failed' | 'requestexception' | 'response' | 'timeout' | 'unknown';

type AccountLinkUpdateErrorMessageCategory = 'cooldown' | 'empty' | 'indexerror' | 'pageempty' | 'requestexception' | 'timeout' | 'unknown';

const accountLinkUpdateErrorCategories = new Set<string>([
    'cooldown',
    'empty',
    'indexerror',
    'pageempty',
    'requestexception',
    'timeout',
]);

const mineracerAccountLinkErrorCategories = new Set<string>([
    'account_not_found',
    'already_linked',
    'expired',
    'identifier_conflict',
    'invalid_device_code',
    'invalid_userid',
    'link_superseded',
    'not_configured',
    'pending_start',
    'remote_failed',
    'requestexception',
    'response',
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

interface AccountLinkBackendErrorResponse {
    type?: string;
    object?: string;
    category?: string;
}

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

export async function startMineracerAccountLinkSession(): Promise<MineracerAccountLinkSession> {
    const { data } = await $axios.post<MineracerAccountLinkSessionResponse>('/api/accountlink/mineracer/start/');
    return new MineracerAccountLinkSession(data);
}

export async function fetchMineracerAccountLinkSession(sessionId: string): Promise<MineracerAccountLinkSession> {
    const { data } = await $axios.get<MineracerAccountLinkSessionResponse>(`/api/accountlink/mineracer/status/${sessionId}`);
    return new MineracerAccountLinkSession(data);
}

export function getAccountLinkUpdateErrorMessageKey(category?: string): string {
    return `accountlink.updateError.${getAccountLinkUpdateErrorMessageCategory(category)}`;
}

export function getMineracerAccountLinkErrorMessageKey(category?: string): string {
    return `accountlink.mineracer.error.${getMineracerAccountLinkErrorMessageCategory(category)}`;
}

export function getMineracerAccountLinkHttpErrorCategory(error: unknown): string | undefined {
    if (!isAxiosError(error)) return undefined;
    const data: unknown = error.response?.data;
    if (!isAccountLinkBackendErrorResponse(data) || data.object !== 'mineracer') return undefined;
    return data.category;
}

function getAccountLinkUpdateErrorMessageCategory(category?: string): AccountLinkUpdateErrorMessageCategory {
    if (category !== undefined && accountLinkUpdateErrorCategories.has(category)) {
        return category as AccountLinkUpdateErrorMessageCategory;
    }
    return 'unknown';
}

function getMineracerAccountLinkErrorMessageCategory(category?: string): MineracerAccountLinkErrorMessageCategory {
    if (category !== undefined && mineracerAccountLinkErrorCategories.has(category)) {
        return category as MineracerAccountLinkErrorMessageCategory;
    }
    return 'unknown';
}

function isAccountLinkBackendErrorResponse(value: unknown): value is AccountLinkBackendErrorResponse {
    return typeof value === 'object' && value !== null;
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
