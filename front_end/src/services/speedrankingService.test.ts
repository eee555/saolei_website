import { afterEach, describe, expect, it, vi } from 'vitest';

import { fetchSpeedRanking, fetchSpeedRecord, formatSpeedValue, isTimeStat, speedVideoId } from './speedrankingService';
import type { SpeedRecord } from './speedrankingService';

import $axios from '@/http';

const record: SpeedRecord = {
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

describe('speedranking', () => {
    afterEach(() => vi.restoreAllMocks());

    it('formats milliseconds, zero values and absent records', () => {
        expect(formatSpeedValue(record, 'bt')).toBe('1.234');
        expect(formatSpeedValue(record, 'bb')).toBe('0.000');
        expect(formatSpeedValue(record, 'et')).toBe('--');
        expect(formatSpeedValue(undefined, 'sumt')).toBe('--');
        expect(speedVideoId(record, 'bt')).toBe(1);
        expect(speedVideoId(record, 'sumt')).toBeUndefined();
        expect(isTimeStat('sumt')).toBe(true);
        expect(isTimeStat('eb')).toBe(false);
    });

    it('passes the selected board and exclusive range to the API', async () => {
        const get = vi.spyOn($axios, 'get').mockResolvedValue({ data: { count: 1, players: [record] } });
        expect(await fetchSpeedRanking('saolei_nf', 'bb', 20, 40)).toEqual({ count: 1, players: [record] });
        expect(get).toHaveBeenCalledWith('/api/speedranking/rank', { params: { board: 'saolei_nf', stat: 'bb', start: 20, end: 40 } });
        get.mockResolvedValue({ data: record });
        expect(await fetchSpeedRecord(42, 'saolei')).toEqual(record);
        expect(get).toHaveBeenLastCalledWith('/api/speedranking/player/42', { params: { board: 'saolei' } });
    });
});
