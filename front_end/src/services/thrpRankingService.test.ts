import { describe, expect, it } from 'vitest';

import { thrpValue } from './thrpRankingService';
import type { ThrpRecord } from './thrpRankingService';

describe('Thrp ranking', () => {
    it('keeps raw values and sums missing levels as zero', () => {
        const record: ThrpRecord = { player_id: 42, b: { value: 1.2345678, video_id: 8001, upload_time: '2026-10-19T12:00:00Z' }, i: null, e: null };
        expect(thrpValue(record, 'b')).toBe(1.2345678);
        expect(thrpValue(record, 'i')).toBeNull();
        expect(thrpValue(record, 'sum')).toBe(1.2345678);
        record.e = { value: 2, video_id: 8002, upload_time: '2026-10-19T12:00:00Z' };
        expect(thrpValue(record, 'sum')).toBeCloseTo(3.2345678, 12);
    });
});
