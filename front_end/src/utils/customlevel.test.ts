import { describe, expect, it } from 'vitest';

import { CustomLevel, DensityCustomLevelConfigs, getDensityCustomLevelByBoard, isDensityCustomLevel } from './customlevel';

describe('CustomLevel', () => {
    describe('constructor', () => {
        it('accepts row, column and mine numbers', () => {
            const level = new CustomLevel(8, 8, 40);

            expect(level.row).toBe(8);
            expect(level.column).toBe(8);
            expect(level.mine).toBe(40);
            expect(level.code).toBe('c8_8_40');
        });

        it('accepts code strings', () => {
            const level = new CustomLevel('c16_30_150');

            expect(level.row).toBe(16);
            expect(level.column).toBe(30);
            expect(level.mine).toBe(150);
            expect(level.code).toBe('c16_30_150');
            expect(level.toString()).toBe('16x30/150');
        });

        it('accepts toString output', () => {
            const level = new CustomLevel('24x30/200');

            expect(level.row).toBe(24);
            expect(level.column).toBe(30);
            expect(level.mine).toBe(200);
            expect(level.code).toBe('c24_30_200');
        });

        it('throws on invalid strings', () => {
            expect(() => new CustomLevel('c8x8x20')).toThrow('Invalid custom level');
            expect(() => new CustomLevel('8_8_20')).toThrow('Invalid custom level');
        });
    });

    it('fromCode returns custom levels only for supported string formats', () => {
        expect(CustomLevel.fromCode('c8_8_40')?.toString()).toBe('8x8/40');
        expect(CustomLevel.fromCode('8x8/40')?.code).toBe('c8_8_40');
        expect(CustomLevel.fromCode('b')).toBeUndefined();
    });

    it('computes derived values', () => {
        const level = new CustomLevel(8, 8, 40);

        expect(level.density).toBe(40 / 64);
        expect(level.boardKey).toBe('8x8x40');
        expect(level.matches(8, 8, 40)).toBe(true);
        expect(level.matches(8, 8, 24)).toBe(false);
    });

    it('compares by row, column, then mine', () => {
        expect(new CustomLevel(8, 8, 40).compare(new CustomLevel(8, 8, 20))).toBeGreaterThan(0);
        expect(new CustomLevel(16, 16, 100).compare(new CustomLevel(24, 30, 200))).toBeLessThan(0);
        expect(new CustomLevel(16, 30, 150).compare(new CustomLevel(16, 30, 150))).toBe(0);
    });
});

describe('density custom level helpers', () => {
    it('contains the configured density levels', () => {
        expect(DensityCustomLevelConfigs).toHaveLength(4);
        expect(DensityCustomLevelConfigs[0].code).toBe('c8_8_40');
        expect(DensityCustomLevelConfigs.at(-1)?.code).toBe('c24_30_200');
    });

    it('finds density custom levels by board', () => {
        expect(getDensityCustomLevelByBoard(16, 30, 150)?.code).toBe('c16_30_150');
        expect(isDensityCustomLevel(16, 30, 150)).toBe(true);
        expect(getDensityCustomLevelByBoard(9, 9, 10)).toBeUndefined();
        expect(isDensityCustomLevel(9, 9, 10)).toBe(false);
    });
});
