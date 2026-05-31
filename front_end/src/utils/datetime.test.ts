import { afterEach, describe, expect, it, vi } from 'vitest';

import {
    arbiterTimeStampToDate,
    fullDay,
    generalTimeStampToDate,
    getWeekTime,
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
