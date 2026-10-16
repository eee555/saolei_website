import { reactive } from 'vue';

import { fetchSaoleiRecords } from './saoleiRankingService';

// Revisions invalidate page data without starting background video downloads.
const revisions = reactive(new Map<number, number>());
const saoleiRecords = new Map<number, ReturnType<typeof fetchSaoleiRecords>>();

export function profileDataRevision(playerId: number): number {
    return revisions.get(playerId) ?? 0;
}

export function invalidateProfileData(playerId: number): void {
    saoleiRecords.delete(playerId);
    revisions.set(playerId, profileDataRevision(playerId) + 1);
}

export function fetchProfileSaoleiRecords(playerId: number): ReturnType<typeof fetchSaoleiRecords> {
    const existing = saoleiRecords.get(playerId);
    if (existing) return existing;
    const request = fetchSaoleiRecords(playerId).catch((error: unknown) => {
        if (saoleiRecords.get(playerId) === request) saoleiRecords.delete(playerId);
        throw error;
    });
    saoleiRecords.set(playerId, request);
    return request;
}
