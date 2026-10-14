import { isAxiosError } from 'axios';

import $axios from '@/http';
import { MineracerAccountLinkSession } from '@/utils/accountlinks';
import type { MineracerAccountLinkSessionResponse } from '@/utils/accountlinks';

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

export function getMineracerAccountLinkHttpErrorCategory(error: unknown): string | undefined {
    if (!isAxiosError(error)) return undefined;
    const data: unknown = error.response?.data;
    if (!isMineracerAccountLinkBackendErrorResponse(data) || data.object !== 'mineracer') return undefined;
    return data.category;
}

function isMineracerAccountLinkBackendErrorResponse(value: unknown): value is MineracerAccountLinkBackendErrorResponse {
    return typeof value === 'object' && value !== null;
}
