import { describe, expect, it } from 'vitest';

import { ArrayUtils } from './arrays';

describe('ArrayUtils', () => {
    describe('range', () => {
        it('Ascending range includes both ends', () => {
            expect(ArrayUtils.range(1, 5)).toEqual([1, 2, 3, 4, 5]);
        });

        it('Descending range supports negative step', () => {
            expect(ArrayUtils.range(5, 1, -2)).toEqual([5, 3, 1]);
        });

        it('Returns empty array when step direction cannot reach end', () => {
            expect(ArrayUtils.range(5, 1)).toEqual([]);
        });
    });

    describe('maximum', () => {
        it('Array', () => {
            expect(ArrayUtils.maximum([3, -4, 9, 2])).toBe(9);
        });

        it('Map iterator', () => {
            const values = new Map([['a', 2], ['b', 7], ['c', 5]]).values();
            expect(ArrayUtils.maximum(values)).toBe(7);
        });

        it('Empty', () => {
            expect(ArrayUtils.maximum([])).toBe(-Infinity);
        });
    });

    describe('minimum', () => {
        it('Array', () => {
            expect(ArrayUtils.minimum([3, -4, 9, 2])).toBe(-4);
        });

        it('Map iterator', () => {
            const values = new Map([['a', 2], ['b', -7], ['c', 5]]).values();
            expect(ArrayUtils.minimum(values)).toBe(-7);
        });

        it('Empty', () => {
            expect(ArrayUtils.minimum([])).toBe(Infinity);
        });
    });

    describe('getInsertIndex', () => {
        it('Ascending', () => {
            expect(ArrayUtils.getInsertIndex([1, 3, 5, 7], 4, true)).toBe(2);
        });

        it('Descending', () => {
            expect(ArrayUtils.getInsertIndex([7, 5, 3, 1], 4, false)).toBe(2);
        });

        it('Duplicate value is inserted before existing matches', () => {
            expect(ArrayUtils.getInsertIndex([1, 3, 3, 5], 3, true)).toBe(1);
        });
    });

    describe('order checks', () => {
        it('Ascending allows equal adjacent values', () => {
            expect(ArrayUtils.isAscending([1, 2, 2, 3])).toBe(true);
        });

        it('Ascending detects descending pair', () => {
            expect(ArrayUtils.isAscending([1, 3, 2])).toBe(false);
        });

        it('Descending allows equal adjacent values', () => {
            expect(ArrayUtils.isDescending([3, 2, 2, 1])).toBe(true);
        });

        it('Descending detects ascending pair', () => {
            expect(ArrayUtils.isDescending([3, 1, 2])).toBe(false);
        });
    });

    describe('array helpers', () => {
        it('empty mutates the original array', () => {
            const arr = [1, 2, 3];
            ArrayUtils.empty(arr);
            expect(arr).toEqual([]);
        });

        it('isEmpty', () => {
            expect(ArrayUtils.isEmpty([])).toBe(true);
            expect(ArrayUtils.isEmpty([1])).toBe(false);
        });

        it('last', () => {
            expect(ArrayUtils.last(['a', 'b'])).toBe('b');
            expect(ArrayUtils.last([])).toBeUndefined();
        });

        it('sortByReferenceOrder sorts subset in place', () => {
            const subset = ['expert', 'beginner', 'intermediate'];
            const sorted = ArrayUtils.sortByReferenceOrder(subset, ['beginner', 'intermediate', 'expert']);

            expect(sorted).toEqual(['beginner', 'intermediate', 'expert']);
            expect(sorted).toBe(subset);
        });
    });
});
