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
    });
});
