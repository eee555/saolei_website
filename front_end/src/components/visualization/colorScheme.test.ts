import { describe, expect, it } from 'vitest';

import { colorSchemeError, colorSchemeIntervals, parseColorScheme, removeColorSchemeThreshold, splitColorScheme } from './colorScheme';

import { PiecewiseColorScheme } from '@/utils/colors';

const colors = ['#112233', 'rgba(0,0,0,0)', '#abcdef'];

describe('color scale editing', () => {
    for (const thresholds of [[10, 20], [20, 10], [10, 10]]) {
        it(`keeps interval symbols consistent with actual boundary colors for ${thresholds.join(',')}`, () => {
            const scheme = { colors, thresholds };
            const intervals = colorSchemeIntervals(scheme);
            const runtime = PiecewiseColorScheme.createFromTheme(scheme);
            for (const value of [0, 9.99, 10, 10.01, 15, 19.99, 20, 20.01, 30]) {
                const matches = intervals.filter((interval) => (interval.lowerClosed ? value >= interval.lower : value > interval.lower)
                    && (interval.upperClosed ? value <= interval.upper : value < interval.upper));
                expect(matches).toHaveLength(1);
                expect(runtime.getColor(value)).toBe(matches[0].color);
            }
        });
    }

    for (const thresholds of [[10, 20], [20, 10]]) {
        it(`switches interval closure by reversing both arrays for ${thresholds.join(',')}`, () => {
            const original = { colors, thresholds };
            const reversed = { colors: [...colors].reverse(), thresholds: [...thresholds].reverse() };
            const before = PiecewiseColorScheme.createFromTheme(original);
            const after = PiecewiseColorScheme.createFromTheme(reversed);
            const originalIntervals = colorSchemeIntervals(original);
            const reversedIntervals = colorSchemeIntervals(reversed);
            expect(reversedIntervals[1].lower).toBe(originalIntervals[1].lower);
            expect(reversedIntervals[1].upper).toBe(originalIntervals[1].upper);
            expect(reversedIntervals[1].lowerClosed).toBe(!originalIntervals[1].lowerClosed);
            expect(reversedIntervals[1].upperClosed).toBe(!originalIntervals[1].upperClosed);
            for (const value of [0, 9.99, 10.01, 15, 19.99, 20.01, 30]) expect(after.getColor(value)).toBe(before.getColor(value));
            for (const threshold of thresholds) expect(after.getColor(threshold)).not.toBe(before.getColor(threshold));
            expect({ colors: [...reversed.colors].reverse(), thresholds: [...reversed.thresholds].reverse() }).toEqual(original);
        });
    }

    it('includes finite domain endpoints and keeps the stored interval order', () => {
        expect(colorSchemeIntervals({ colors, thresholds: [20, 10] }, 0, 100)).toEqual([
            { index: 0, color: '#112233', lower: 20, upper: 100, lowerClosed: true, upperClosed: true },
            { index: 1, color: 'rgba(0,0,0,0)', lower: 10, upper: 20, lowerClosed: true, upperClosed: false },
            { index: 2, color: '#abcdef', lower: 0, upper: 10, lowerClosed: true, upperClosed: false },
        ]);
    });

    it('imports both directions and existing transparent colors without rewriting them', () => {
        for (const thresholds of [[10, 20], [20, 10]]) {
            const scheme = { thresholds, colors: ['rgba(255,255,255,0)', 'rgba(0,0,0,0)', '#abcdef'] };
            expect(parseColorScheme(JSON.stringify(scheme))).toEqual(scheme);
        }
    });

    it('rejects malformed JSON, wrong lengths, unsorted or out-of-range thresholds and invalid colors', () => {
        expect(() => parseColorScheme('[,')).toThrow(SyntaxError);
        for (const value of [null, [], {}, { colors: colors, thresholds: [10] }]) expect(colorSchemeError(value)).toBe('invalidShape');
        expect(colorSchemeError({ colors, thresholds: [NaN, 20] })).toBe('invalidThresholds');
        expect(colorSchemeError({ colors, thresholds: [10, Infinity] })).toBe('invalidThresholds');
        expect(colorSchemeError({ colors, thresholds: [-1, 10] }, 0, 100)).toBe('invalidThresholds');
        expect(colorSchemeError({ colors: [...colors, '#000000'], thresholds: [10, 30, 20] })).toBe('unsortedThresholds');
        expect(colorSchemeError({ colors: ['not-a-color', '#000000', '#ffffff'], thresholds: [10, 20] })).toBe('invalidColors');
        expect(colorSchemeError({ colors: [null, '#000000', '#ffffff'], thresholds: [10, 20] })).toBe('invalidColors');
    });

    for (const thresholds of [[10, 20], [20, 10]]) {
        it(`splits every interval in ${thresholds.join(',')} without mutating the original`, () => {
            const scheme = { colors: [...colors], thresholds: [...thresholds] };
            for (const index of [0, 1, 2]) {
                const split = splitColorScheme(scheme, index, 0, 100);
                expect(split).not.toBeNull();
                if (split === null) throw new Error('Expected a split');
                expect(colorSchemeError(split, 0, 100)).toBeNull();
                expect(split.colors[index + 1]).toBe(scheme.colors[index]);
                expect(removeColorSchemeThreshold(split, index)).toEqual(scheme);
            }
            expect(scheme).toEqual({ colors, thresholds });
        });
    }

    it('does not split zero-width intervals and can add an initial boundary', () => {
        expect(splitColorScheme({ colors, thresholds: [10, 10] }, 1)).toBeNull();
        expect(splitColorScheme({ colors: ['rgba(0,0,0,0)'], thresholds: [] }, 0, 0, 100)).toEqual({ colors: ['rgba(0,0,0,0)', 'rgba(0,0,0,0)'], thresholds: [50] });
    });
});
