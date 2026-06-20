import { describe, expect, it } from 'vitest';

import { clamp, getLastDigit, setLastDigit } from './math';

describe('math', () => {
    describe('getLastDigit', () => {
        it('Positive number', () => {
            expect(getLastDigit(1234)).toBe(4);
        });

        it('Negative number keeps JavaScript remainder sign', () => {
            expect(getLastDigit(-1234)).toBe(-4);
        });
    });

    describe('setLastDigit', () => {
        it('Replaces last digit', () => {
            expect(setLastDigit(1234, 9)).toBe(1239);
        });

        it('Works with zero last digit', () => {
            expect(setLastDigit(1200, 7)).toBe(1207);
        });
    });

    describe('clamp', () => {
        it('keeps value within range', () => {
            expect(clamp(5, 1, 10)).toBe(5);
        });

        it('returns min when value is too small', () => {
            expect(clamp(-1, 1, 10)).toBe(1);
        });

        it('returns max when value is too large', () => {
            expect(clamp(11, 1, 10)).toBe(10);
        });
    });
});
