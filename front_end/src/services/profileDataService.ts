import { reactive } from 'vue';

import { fetchSaoleiRecords } from './saoleiRankingService';
import { fetchThrpRecord } from './thrpRankingService';

// Revisions invalidate page data without starting background video downloads.
const revisions = reactive(new Map<number, number>());
const saoleiRecords = new Map<number, ReturnType<typeof fetchSaoleiRecords>>();
const thrpRecords = new Map<number, ReturnType<typeof fetchThrpRecord>>();

export function profileDataRevision(playerId: number): number {
    return revisions.get(playerId) ?? 0;
}

export function invalidateProfileData(playerId: number): void {
    saoleiRecords.delete(playerId);
    thrpRecords.delete(playerId);
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

export function fetchProfileThrpRecord(playerId: number): ReturnType<typeof fetchThrpRecord> {
    const existing = thrpRecords.get(playerId);
    if (existing) return existing;
    const request = fetchThrpRecord(playerId).catch((error: unknown) => {
        if (thrpRecords.get(playerId) === request) thrpRecords.delete(playerId);
        throw error;
    });
    thrpRecords.set(playerId, request);
    return request;
}
