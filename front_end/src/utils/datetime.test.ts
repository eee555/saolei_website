import { afterEach, describe, expect, it, vi } from 'vitest';

import {
    arbiterTimeStampToDate,
    fullDay,
    generalTimeStampToDate,
    generateDateRange,
    getWeekTime,
    toDate,
    toISODateString,
    toISODateTimeString,
} from './datetime';

describe('datetime', () => {
    afterEach(() => {
        vi.useRealTimers();
    });

    describe('getWeekTime', () => {
        it('Subtracts day offset from date timestamp', () => {
            const date = new Date(2025, 5, 18, 12, 30, 0);

            expect(getWeekTime(date)).toBe(date.getTime() - date.getDay() * fullDay);
        });
    });

    describe('toDate', () => {
        it('Creates dates from supported Date constructor inputs', () => {
            const date = new Date('2025-01-05T08:09:10Z');

            expect(toDate('2025-01-05T08:09:10Z')).toEqual(date);
            expect(toDate(date.getTime())).toEqual(date);
            expect(toDate(date)).toEqual(date);
            expect(toDate(date)).not.toBe(date);
        });

        it('Returns undefined for nullish inputs', () => {
            expect(toDate(null)).toBeUndefined();
            expect(toDate(undefined)).toBeUndefined();
        });
    });

    describe('toISODateString', () => {
        it('Formats local date with padded month and day', () => {
            expect(toISODateString(new Date(2025, 0, 5, 8, 9, 10))).toBe('2025-01-05');
        });
    });

    describe('toISODateTimeString', () => {
        it('Formats local date and time with padded fields', () => {
            expect(toISODateTimeString(new Date(2025, 0, 5, 8, 9, 10))).toBe('2025-01-05 08:09:10');
        });
    });

    describe('generateDateRange', () => {
        it('Generates dates from start to end inclusively', () => {
            const dates = Array.from(generateDateRange(new Date(2025, 0, 1), new Date(2025, 0, 3)));

            expect(dates).toEqual([
                new Date(2025, 0, 1),
                new Date(2025, 0, 2),
                new Date(2025, 0, 3),
            ]);
        });

        it('Supports custom day steps', () => {
            const dates = Array.from(generateDateRange(new Date(2025, 0, 1), new Date(2025, 0, 7), 2));

            expect(dates).toEqual([
                new Date(2025, 0, 1),
                new Date(2025, 0, 3),
                new Date(2025, 0, 5),
                new Date(2025, 0, 7),
            ]);
        });

        it('Does not mutate the input dates or reuse yielded date objects', () => {
            const startDate = new Date(2025, 0, 1);
            const endDate = new Date(2025, 0, 2);
            const dates = Array.from(generateDateRange(startDate, endDate));

            dates[0].setFullYear(2030);

            expect(startDate).toEqual(new Date(2025, 0, 1));
            expect(endDate).toEqual(new Date(2025, 0, 2));
            expect(dates[1]).toEqual(new Date(2025, 0, 2));
        });

        it('Returns an empty range when start is after end', () => {
            expect(Array.from(generateDateRange(new Date(2025, 0, 3), new Date(2025, 0, 1)))).toEqual([]);
        });
    });

    describe('generalTimeStampToDate', () => {
        it('Converts microsecond timestamp to date', () => {
            expect(generalTimeStampToDate(BigInt(1700000000000000))).toEqual(new Date(1700000000000));
        });
    });

    describe('arbiterTimeStampToDate', () => {
        it('Applies local timezone offset to microsecond timestamp', () => {
            vi.useFakeTimers();
            vi.setSystemTime(new Date('2025-06-15T12:00:00Z'));

            const timestamp = BigInt(1700000000000000);
            const expected = new Date(1700000000000 + new Date().getTimezoneOffset() * 60000);

            expect(arbiterTimeStampToDate(timestamp)).toEqual(expected);
        });
    });
});
