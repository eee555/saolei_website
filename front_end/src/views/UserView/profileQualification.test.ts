import { beforeEach, describe, expect, it, vi } from 'vitest';

import { invalidateProfileData } from '@/services/profileDataService';
import { fetchSaoleiRecords } from '@/services/saoleiRankingService';
import type { SaoleiPlayerRecord, SaoleiRankingName } from '@/services/saoleiRankingService';
import { store } from '@/store';

vi.mock('@/services/saoleiRankingService', () => ({ fetchSaoleiRecords: vi.fn() }));
vi.mock('@/store/local', () => ({ local: { value: {} } }));
const makeRecord = (et: number | null) => ({ saolei: { et } } as Record<SaoleiRankingName, SaoleiPlayerRecord>);

describe('profile avatar/signature eligibility', () => {
    beforeEach(() => {
        vi.resetAllMocks();
        invalidateProfileData(42);
        invalidateProfileData(43);
        store.login({ id: 42 });
    });

    it('uses the normal saolei record without loading any videos, including an absent expert record', async () => {
        vi.mocked(fetchSaoleiRecords).mockResolvedValue(makeRecord(35090));
        await store.loadQualification();
        expect(store.expTimeMs).toBe(35090);
        expect(store.qualificationStatus).toBe('ready');
        expect(store.user.videos).toBeUndefined();
        invalidateProfileData(42);
        vi.mocked(fetchSaoleiRecords).mockResolvedValue(makeRecord(null));
        await store.loadQualification();
        expect(store.expTimeMs).toBeGreaterThanOrEqual(200000);
        expect(store.qualificationStatus).toBe('ready');
    });

    it('ignores a previous session response and does not clear the current loading status', async () => {
        const previous = Promise.withResolvers<Record<SaoleiRankingName, SaoleiPlayerRecord>>();
        const current = Promise.withResolvers<Record<SaoleiRankingName, SaoleiPlayerRecord>>();
        vi.mocked(fetchSaoleiRecords).mockReturnValueOnce(previous.promise).mockReturnValueOnce(current.promise);
        const oldLoad = store.loadQualification();
        store.login({ id: 43 });
        const newLoad = store.loadQualification();
        previous.resolve(makeRecord(1000));
        await oldLoad;
        expect(store.qualificationStatus).toBe('loading');
        expect(store.expertTimeMs).toBeUndefined();
        current.resolve(makeRecord(240000));
        await newLoad;
        expect(store.expTimeMs).toBe(240000);
        expect(store.qualificationStatus).toBe('ready');
    });

    it('distinguishes request failure from an ineligible record and permits retry', async () => {
        vi.mocked(fetchSaoleiRecords).mockRejectedValueOnce(new Error('network')).mockResolvedValueOnce(makeRecord(199999));
        await store.loadQualification();
        expect(store.qualificationStatus).toBe('error');
        expect(store.expertTimeMs).toBeUndefined();
        await store.loadQualification();
        expect(store.qualificationStatus).toBe('ready');
        expect(store.expTimeMs).toBe(199999);
    });
});
