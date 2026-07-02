import { describe, expect, it } from 'vitest';

import { CustomLevel, DensityCustomLevelConfigs, getDensityCustomLevelByBoard, isDensityCustomLevel } from './customlevel';

describe('CustomLevel', () => {
    describe('constructor', () => {
        it('accepts row, column and mine numbers', () => {
            const level = new CustomLevel(8, 8, 20);

            expect(level.row).toBe(8);
            expect(level.column).toBe(8);
            expect(level.mine).toBe(20);
            expect(level.code).toBe('c8_8_20');
        });

        it('accepts code strings', () => {
            const level = new CustomLevel('c16_30_144');

            expect(level.row).toBe(16);
            expect(level.column).toBe(30);
            expect(level.mine).toBe(144);
            expect(level.code).toBe('c16_30_144');
            expect(level.toString()).toBe('16x30/144');
        });

        it('accepts toString output', () => {
            const level = new CustomLevel('24x30/216');

            expect(level.row).toBe(24);
            expect(level.column).toBe(30);
            expect(level.mine).toBe(216);
            expect(level.code).toBe('c24_30_216');
        });

        it('throws on invalid strings', () => {
            expect(() => new CustomLevel('c8x8x20')).toThrow('Invalid custom level');
            expect(() => new CustomLevel('8_8_20')).toThrow('Invalid custom level');
        });
    });

    it('fromCode returns custom levels only for supported string formats', () => {
        expect(CustomLevel.fromCode('c8_8_20')?.toString()).toBe('8x8/20');
        expect(CustomLevel.fromCode('8x8/20')?.code).toBe('c8_8_20');
        expect(CustomLevel.fromCode('b')).toBeUndefined();
    });

    it('computes derived values', () => {
        const level = new CustomLevel(8, 8, 20);

        expect(level.density).toBe(20 / 64);
        expect(level.boardKey).toBe('8x8x20');
        expect(level.matches(8, 8, 20)).toBe(true);
        expect(level.matches(8, 8, 24)).toBe(false);
    });

    it('compares by row, column, then mine', () => {
        expect(new CustomLevel(8, 8, 24).compare(new CustomLevel(8, 8, 20))).toBeGreaterThan(0);
        expect(new CustomLevel(16, 16, 64).compare(new CustomLevel(24, 30, 180))).toBeLessThan(0);
        expect(new CustomLevel(16, 30, 144).compare(new CustomLevel(16, 30, 144))).toBe(0);
    });
});

describe('density custom level helpers', () => {
    it('contains the configured density levels', () => {
        expect(DensityCustomLevelConfigs).toHaveLength(19);
        expect(DensityCustomLevelConfigs[0].code).toBe('c8_8_20');
        expect(DensityCustomLevelConfigs.at(-1)?.code).toBe('c48_64_777');
    });

    it('finds density custom levels by board', () => {
        expect(getDensityCustomLevelByBoard(16, 30, 144)?.code).toBe('c16_30_144');
        expect(isDensityCustomLevel(16, 30, 144)).toBe(true);
        expect(getDensityCustomLevelByBoard(9, 9, 10)).toBeUndefined();
        expect(isDensityCustomLevel(9, 9, 10)).toBe(false);
    });
});
