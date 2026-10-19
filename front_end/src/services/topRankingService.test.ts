import { describe, expect, it } from 'vitest';

import { formatTopValue, topAxes, topEquivalentEt, topField, topGrade, topLsfContributions, topMean, topRadius, topSoftValues } from './topRankingService';
import type { TopAnchors, TopRecords } from './topRankingService';

describe('top ranking', () => {
    it('formats raw time, bvs and iqg without changing their values', () => {
        expect(formatTopValue(1234.2, 'b', 't')).toBe('1.234');
        expect(formatTopValue(2, 'b', 'b')).toBe('2.000');
        expect(formatTopValue(2, 'b', 's')).toBe('72.000');
        expect(formatTopValue(2, 'i', 's')).toBe('324.000');
        expect(formatTopValue(2, 'e', 's')).toBe('870.000');
        expect(formatTopValue(0, 'b', 's')).toBe('0.000');
    });

    it('normalizes player values against the chart anchor without capping', () => {
        expect(topRadius(2000, 1000, 't')).toBe(50);
        expect(topRadius(1000, 2000, 't')).toBe(200);
        expect(topRadius(4, 2, 'b')).toBe(200);
        expect(topRadius(4, 2, 's')).toBeCloseTo(100 * 2 ** (1 / 1.7));
        for (const stat of ['t', 'b', 's'] as const) {
            expect(topRadius(2, 2, stat)).toBe(100);
            expect(topRadius(0, 0, stat)).toBe(0);
        }
    });

    it('converts strength scales to equivalent seconds using the matching ordinary or NF expert anchor', () => {
        const anchors: TopAnchors = { 'std:et': { value: 30000, sample_count: 20 }, 'nf:et': { value: 60000, sample_count: 20 } };
        expect(topEquivalentEt(1, anchors)).toBe(30);
        expect(topEquivalentEt(150, anchors, 100)).toBe(20);
        expect(topEquivalentEt(50, anchors, 100)).toBe(60);
        expect(topEquivalentEt(4000, anchors, 4000)).toBe(30);
        expect(topEquivalentEt(1, anchors, 1, true)).toBe(60);
        expect(topEquivalentEt(0, anchors)).toBe(Infinity);
        expect(topEquivalentEt(1, { 'std:et': { value: 0, sample_count: 0 } })).toBeNull();
        expect(topEquivalentEt(1, { 'std:et': anchors['std:et'] }, 1, true)).toBeNull();
    });

    it('grades strength linearly with stronger boundary intervals and uncapped final stages', () => {
        const anchors: TopAnchors = { 'std:et': { value: 30000, sample_count: 20 }, 'nf:et': { value: 60000, sample_count: 20 } };
        expect(topGrade(0, anchors)).toEqual({ index: 0, position: 0 });
        for (const [index, seconds] of [100, 60, 55, 50, 45, 40, 35, 30].entries()) {
            const grade = topGrade(30 / seconds, anchors);
            expect(grade?.index).toBe(index + 1);
            expect(grade?.position).toBeCloseTo(0);
        }
        expect(topGrade(0.15, anchors)).toEqual({ index: 0, position: 0.5 });
        expect(topGrade(30 / 27.5, anchors)?.position).toBeCloseTo(0.454545);
        expect(topGrade(1.2, anchors)?.position).toBeCloseTo(1);
        expect(topGrade(1.5, anchors)?.position).toBeCloseTo(2.5);
        expect(topGrade(150, anchors, 100)).toEqual(topGrade(6000, anchors, 4000));
        expect(topGrade(100, anchors, 100, true)).toEqual({ index: 2, position: 0 });
        expect(topGrade(1, {})).toBeNull();
        expect(topGrade(1, { 'std:et': { value: 0, sample_count: 0 } })).toBeNull();
        expect(topGrade(1, { 'std:et': anchors['std:et'] }, 1, true)).toBeNull();
    });

    it('reconstructs padded means and all nine soft values from the raw five videos', () => {
        expect(topMean(undefined, 't')).toBe(999999);
        expect(topMean({ videos: [{ value: 1000, video_id: 1 }] }, 't')).toBe((1000 + 4 * 999999) / 5);
        expect(topMean(undefined, 's')).toBe(0);
        const records: TopRecords = {};
        const anchors: TopAnchors = {};
        for (const nf of [false, true]) {
            for (const { level, stat } of topAxes) {
                const field = topField(nf, level, stat);
                const value = stat === 't' ? 1000 : 2;
                records[field] = { videos: Array.from({ length: 5 }, (_, id) => ({ value, video_id: id + 1 })) };
                anchors[field] = { value, sample_count: 20 };
            }
        }
        const values = topSoftValues(records, anchors);
        expect(values).toEqual({ lsf: 4000, 'std:b': 100, 'std:i': 100, 'std:e': 100, 'std:sum': 4000, 'nf:b': 100, 'nf:i': 100, 'nf:e': 100, 'nf:sum': 4000 });
        expect(topLsfContributions(values).map((part) => part.value)).toEqual([582, 1358, 1940, 18, 42, 60]);
        records['std:bt'] = { videos: Array.from({ length: 5 }, (_, id) => ({ value: 500, video_id: id + 1 })) };
        const improved = topSoftValues(records, anchors);
        expect(improved.lsf).toBeCloseTo(4000 + 28 * 6 * 0.97);
        expect(topLsfContributions(improved).reduce((total, part) => total + part.value, 0)).toBeCloseTo(improved.lsf);
    });
});
