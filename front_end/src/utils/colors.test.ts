import { describe, expect, it } from 'vitest';

import { PiecewiseColorScheme } from './colors';

describe('PiecewiseColorScheme', () => {
    describe('constructor', () => {
        it('Rejects unsorted thresholds', () => {
            expect(() => new PiecewiseColorScheme(['a', 'b', 'c'], [2, 1, 3])).toThrow('Thresholds must be either ascending or descending');
        });
    });

    describe('createFromTheme', () => {
        it('Creates color scheme from theme object', () => {
            const scheme = PiecewiseColorScheme.createFromTheme({
                thresholds: [10, 20],
                colors: ['low', 'middle', 'high'],
            });

            expect(scheme.getColor(15)).toBe('middle');
        });
    });

    describe('getColor', () => {
        it('Ascending thresholds', () => {
            const scheme = new PiecewiseColorScheme(['low', 'middle', 'high'], [10, 20]);

            expect(scheme.getColor(5)).toBe('low');
            expect(scheme.getColor(10)).toBe('low');
            expect(scheme.getColor(15)).toBe('middle');
            expect(scheme.getColor(25)).toBe('high');
        });

        it('Descending thresholds', () => {
            const scheme = new PiecewiseColorScheme(['fast', 'normal', 'slow'], [20, 10]);

            expect(scheme.getColor(25)).toBe('fast');
            expect(scheme.getColor(20)).toBe('fast');
            expect(scheme.getColor(15)).toBe('normal');
            expect(scheme.getColor(5)).toBe('slow');
        });

        it('Returns transparent color for NaN', () => {
            const scheme = new PiecewiseColorScheme(['low', 'high'], [10]);

            expect(scheme.getColor(NaN)).toBe('rgba(0,0,0,0)');
        });

        it('Returns transparent color when the computed bucket has no color', () => {
            const scheme = new PiecewiseColorScheme(['low'], [10]);

            expect(scheme.getColor(15)).toBe('rgba(0,0,0,0)');
        });
    });

    describe('getStyle', () => {
        it('Returns precomputed background and readable text colors', () => {
            const scheme = new PiecewiseColorScheme(['#ffffff', '#000000'], [10]);

            expect(scheme.getStyle(5)).toEqual({ backgroundColor: '#ffffff', color: 'black' });
            expect(scheme.getStyle(15)).toEqual({ backgroundColor: '#000000', color: 'white' });
        });

        it('Reuses style objects for the same color bucket', () => {
            const scheme = new PiecewiseColorScheme(['#ffffff', '#000000'], [10]);

            expect(scheme.getStyle(5)).toBe(scheme.getStyle(10));
        });

        it('Returns an empty style without overriding inherited styles for NaN', () => {
            const scheme = new PiecewiseColorScheme(['#ffffff', '#000000'], [10]);

            expect(scheme.getStyle(NaN)).toEqual({});
        });

        it('Does not override inherited text color for transparent color buckets', () => {
            const scheme = new PiecewiseColorScheme(['rgba(255,255,255,0)', '#000000'], [10]);

            expect(scheme.getStyle(5)).toEqual({});
        });

        it('Falls back to the empty style when the computed bucket has no style', () => {
            const scheme = new PiecewiseColorScheme(['#ffffff'], [10]);

            expect(scheme.getStyle(15)).toStrictEqual(scheme.getStyle(NaN));
            expect(scheme.getStyle(15)).toEqual({});
        });
    });
});
