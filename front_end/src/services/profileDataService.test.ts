import { beforeEach, describe, expect, it, vi } from 'vitest';

import { fetchProfileSaoleiRecords, invalidateProfileData, profileDataRevision } from './profileDataService';
import { fetchSaoleiRecords } from './saoleiRankingService';
import type { SaoleiPlayerRecord, SaoleiRankingName } from './saoleiRankingService';

vi.mock('./saoleiRankingService', () => ({ fetchSaoleiRecords: vi.fn() }));

describe('profile record cache', () => {
    beforeEach(() => {
        vi.resetAllMocks();
        invalidateProfileData(42);
    });

    it('shares pending and completed lightweight records, and invalidates without downloading', async () => {
        const data = {} as Record<SaoleiRankingName, SaoleiPlayerRecord>;
        vi.mocked(fetchSaoleiRecords).mockResolvedValue(data);
        const first = fetchProfileSaoleiRecords(42);
        expect(fetchProfileSaoleiRecords(42)).toBe(first);
        await first;
        expect(await fetchProfileSaoleiRecords(42)).toBe(data);
        expect(fetchSaoleiRecords).toHaveBeenCalledTimes(1);
        const version = profileDataRevision(42);
        invalidateProfileData(42);
        expect(profileDataRevision(42)).toBe(version + 1);
        expect(fetchSaoleiRecords).toHaveBeenCalledTimes(1);
        await fetchProfileSaoleiRecords(42);
        expect(fetchSaoleiRecords).toHaveBeenCalledTimes(2);
    });

    it('allows retrying failures without deleting a newer request during invalidation', async () => {
        const old = Promise.withResolvers<Record<SaoleiRankingName, SaoleiPlayerRecord>>();
        vi.mocked(fetchSaoleiRecords).mockReturnValueOnce(old.promise).mockResolvedValue({} as Record<SaoleiRankingName, SaoleiPlayerRecord>);
        const previous = fetchProfileSaoleiRecords(42);
        const rejected = expect(previous).rejects.toThrow('old request');
        invalidateProfileData(42);
        const current = fetchProfileSaoleiRecords(42);
        old.reject(new Error('old request'));
        await rejected;
        expect(fetchProfileSaoleiRecords(42)).toBe(current);
        invalidateProfileData(42);
        vi.mocked(fetchSaoleiRecords).mockRejectedValueOnce(new Error('network'));
        await expect(fetchProfileSaoleiRecords(42)).rejects.toThrow('network');
        await fetchProfileSaoleiRecords(42);
        expect(fetchSaoleiRecords).toHaveBeenCalledTimes(4);
    });
});
