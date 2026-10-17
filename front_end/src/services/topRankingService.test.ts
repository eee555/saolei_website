import { describe, expect, it } from 'vitest';

import { formatTopValue, missingTopValue, topRadius } from './topRankingService';

describe('top ranking', () => {
    it('formats raw time, bvs and iqg without changing their values', () => {
        expect(formatTopValue(1234.2, 'b', 't')).toBe('1.234');
        expect(formatTopValue(2, 'b', 'b')).toBe('2.000');
        expect(formatTopValue(2, 'b', 's')).toBe('72.000');
        expect(formatTopValue(2, 'i', 's')).toBe('324.000');
        expect(formatTopValue(2, 'e', 's')).toBe('870.000');
        expect(formatTopValue(0, 'b', 's')).toBe('0.000');
        expect(missingTopValue('t')).toBe(999999);
        expect(missingTopValue('s')).toBe(0);
    });

    it('normalizes player values against the chart anchor without capping', () => {
        expect(topRadius(2000, 1000, 't')).toBe(50);
        expect(topRadius(1000, 2000, 't')).toBe(200);
        expect(topRadius(4, 2, 'b')).toBe(200);
        expect(topRadius(4, 2, 's')).toBe(200);
        for (const stat of ['t', 'b', 's'] as const) {
            expect(topRadius(2, 2, stat)).toBe(100);
            expect(topRadius(0, 0, stat)).toBe(0);
        }
    });
});
