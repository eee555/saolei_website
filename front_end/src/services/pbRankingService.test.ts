import { afterEach, describe, expect, it, vi } from 'vitest';

import { fetchPBCounts, fetchPBRanking, formatPBUploadTime, formatPBValue, pbBVLimits, pbLevels } from './pbRankingService';

import $axios from '@/http';

describe('PB ranking', () => {
    afterEach(() => vi.restoreAllMocks());

    it('formats time, derived statistics and minute-precision upload dates', () => {
        expect(formatPBValue(1234, 'b', 4, 'time')).toBe('1.234');
        expect(formatPBValue(2000, 'b', 4, 'bvs')).toBe('2.000');
        for (const level of pbLevels) {
            const coefficient = { b: 36, i: 162, e: 435 }[level];
            expect(formatPBValue(2000, level, 4, 'stnb')).toBe((coefficient * 4 / 2 ** 1.7).toFixed(3));
            expect(formatPBValue(0, level, 1, 'bvs')).toBe('Infinity');
            expect(formatPBValue(0, level, 1, 'stnb')).toBe('Infinity');
        }
        const upload = new Date(2026, 9, 5, 12, 34, 0);
        expect(formatPBUploadTime(upload.toISOString())).toBe('2026-10-05 12:34');
        expect(pbBVLimits).toEqual({ b: { min: 1, max: 54 }, i: { min: 1, max: 216 }, e: { min: 1, max: 381 } });
    });

    it('requests one selected bucket using an exclusive rank range', async () => {
        const data = { count: 21, players: [{ player_id: 48, video_id: 123, timems: 1234, upload_time: '2026-10-05T12:34:00Z' }] };
        const get = vi.spyOn($axios, 'get').mockResolvedValue({ data });
        expect(await fetchPBRanking('e', 381, true, 20, 40)).toEqual(data);
        expect(get).toHaveBeenCalledExactlyOnceWith('/api/speedranking/pb/rank', { params: { level: 'e', bv: 381, nf: true, start: 20, end: 40 } });
        const counts = { 'std:b:1': 21, 'nf:b:1': 7 };
        get.mockClear().mockResolvedValue({ data: counts });
        expect(await fetchPBCounts()).toEqual(counts);
        expect(get).toHaveBeenCalledExactlyOnceWith('/api/speedranking/pb/counts');
    });
});
