import { afterEach, describe, expect, it, vi } from 'vitest';

import { fetchSaoleiRanking, fetchSaoleiRecord, formatSaoleiValue, isSaoleiTimeStat, saoleiVideoId } from './saoleiRankingService';
import type { SaoleiRecord } from './saoleiRankingService';

import $axios from '@/http';

const record: SaoleiRecord = {
    player_id: 42,
    bt: 1234,
    bb: 0,
    it: null,
    ib: null,
    et: null,
    eb: null,
    sumt: 2001232,
    sumb: 0,
    bt_id: 1,
    bb_id: 2,
    it_id: null,
    ib_id: null,
    et_id: null,
    eb_id: null,
};

describe('saoleiRanking', () => {
    afterEach(() => vi.restoreAllMocks());

    it('formats milliseconds, zero values and absent records', () => {
        expect(formatSaoleiValue(record, 'bt')).toBe('1.234');
        expect(formatSaoleiValue(record, 'bb')).toBe('0.000');
        expect(formatSaoleiValue(record, 'et')).toBe('--');
        expect(formatSaoleiValue(record, 'sumt')).toBe('2001.232');
        expect(formatSaoleiValue(record, 'sumb')).toBe('0.000');
        expect(formatSaoleiValue(undefined, 'sumt')).toBe('--');
        expect(saoleiVideoId(record, 'bt')).toBe(1);
        expect(saoleiVideoId(record, 'sumt')).toBeUndefined();
        expect(saoleiVideoId(record, 'sumb')).toBeUndefined();
        expect(saoleiVideoId(record, 'et')).toBeUndefined();
        expect(isSaoleiTimeStat('sumt')).toBe(true);
        expect(isSaoleiTimeStat('eb')).toBe(false);
    });

    it('passes the selected board and exclusive range to the API', async () => {
        const get = vi.spyOn($axios, 'get').mockResolvedValue({ data: { count: 1, players: [record] } });
        expect(await fetchSaoleiRanking('saolei_nf', 'bb', 20, 40)).toEqual({ count: 1, players: [record] });
        expect(get).toHaveBeenCalledWith('/api/speedranking/rank', { params: { board: 'saolei_nf', stat: 'bb', start: 20, end: 40 } });
        get.mockResolvedValue({ data: record });
        expect(await fetchSaoleiRecord(42, 'saolei')).toEqual(record);
        expect(get).toHaveBeenLastCalledWith('/api/speedranking/player/42', { params: { board: 'saolei' } });
    });
});
