import { isAxiosError } from 'axios';

import $axios from '@/http';
import { MineracerAccountLinkSession } from '@/utils/accountlinks';
import type { MineracerAccountLinkSessionResponse } from '@/utils/accountlinks';

type MineracerAccountLinkErrorMessageCategory = 'account_not_found' | 'already_linked' | 'expired' | 'identifier_conflict' | 'invalid_device_code' | 'invalid_userid' | 'link_superseded' | 'not_configured' | 'pending_start' | 'remote_failed' | 'requestexception' | 'response' | 'timeout' | 'unknown';

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

interface MineracerAccountLinkBackendErrorResponse {
    type?: string;
    object?: string;
    category?: string;
}

export async function startMineracerAccountLinkSession(): Promise<MineracerAccountLinkSession> {
    const { data } = await $axios.post<MineracerAccountLinkSessionResponse>('/api/accountlink/mineracer/start/');
    return new MineracerAccountLinkSession(data);
}

export async function fetchMineracerAccountLinkSession(sessionId: string): Promise<MineracerAccountLinkSession> {
    const { data } = await $axios.get<MineracerAccountLinkSessionResponse>(`/api/accountlink/mineracer/status/${sessionId}`);
    return new MineracerAccountLinkSession(data);
}

export function getMineracerAccountLinkErrorMessageKey(category?: string): string {
    return `accountlink.mineracer.error.${getMineracerAccountLinkErrorMessageCategory(category)}`;
}

export function getMineracerAccountLinkHttpErrorCategory(error: unknown): string | undefined {
    if (!isAxiosError(error)) return undefined;
    const data: unknown = error.response?.data;
    if (!isMineracerAccountLinkBackendErrorResponse(data) || data.object !== 'mineracer') return undefined;
    return data.category;
}

function getMineracerAccountLinkErrorMessageCategory(category?: string): MineracerAccountLinkErrorMessageCategory {
    if (category !== undefined && mineracerAccountLinkErrorCategories.has(category)) {
        return category as MineracerAccountLinkErrorMessageCategory;
    }
    return 'unknown';
}

function isMineracerAccountLinkBackendErrorResponse(value: unknown): value is MineracerAccountLinkBackendErrorResponse {
    return typeof value === 'object' && value !== null;
}
