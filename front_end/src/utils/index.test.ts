import { afterEach, describe, expect, it, vi } from 'vitest';

import {
    createEnumMap,
    cs_to_s,
    deepCopy,
    deepMutableCopy,
    ms_to_s,
    sleep,
    to_fixed_n,
} from './index';

describe('utils index', () => {
    afterEach(() => {
        vi.useRealTimers();
    });

    describe('deepMutableCopy', () => {
        it('deep clones objects and returns mutable nested data', () => {
            const source: {
                readonly nested: { readonly count: number };
                readonly list: readonly { readonly name: string }[];
            } = {
                nested: { count: 1 },
                list: [{ name: 'first' }],
            };

            const copy = deepMutableCopy(source);
            copy.nested.count = 2;
            copy.list[0].name = 'changed';
            copy.list.push({ name: 'second' });

            expect(copy).toEqual({
                nested: { count: 2 },
                list: [{ name: 'changed' }, { name: 'second' }],
            });
            expect(source).toEqual({
                nested: { count: 1 },
                list: [{ name: 'first' }],
            });
        });
    });

    describe('createEnumMap', () => {
        it('creates entries for every key and deep clones the default value', () => {
            const map = createEnumMap(['beginner', 'expert'] as const, {
                enabled: true,
                values: [1, 2],
            });

            map.beginner.values.push(3);
            map.expert.enabled = false;

            expect(map).toEqual({
                beginner: { enabled: true, values: [1, 2, 3] },
                expert: { enabled: false, values: [1, 2] },
            });
            expect(map.beginner.values).not.toBe(map.expert.values);
        });
    });

    describe('to_fixed_n', () => {
        it('formats numeric and string inputs with fixed digits', () => {
            expect(to_fixed_n(1.23456, 3)).toBe('1.235');
            expect(to_fixed_n('2.3456', 2)).toBe('2.35');
            expect(to_fixed_n(-1.23456, 3)).toBe('-1.235');
            expect(to_fixed_n('-2.3456', 2)).toBe('-2.35');
        });

        it('returns undefined and non-positive precision inputs unchanged', () => {
            expect(to_fixed_n(undefined, 3)).toBeUndefined();
            expect(to_fixed_n(1.234, 0)).toBe(1.234);
            expect(to_fixed_n('1.234', -1)).toBe('1.234');
        });
    });

    describe('time formatters', () => {
        it('formats milliseconds as seconds with three decimals', () => {
            expect(ms_to_s(undefined)).toBe('-');
            expect(ms_to_s(0)).toBe('0.000');
            expect(ms_to_s(9)).toBe('0.009');
            expect(ms_to_s(12345)).toBe('12.345');
            expect(ms_to_s(-9)).toBe('-0.009');
            expect(ms_to_s(-12345)).toBe('-12.345');
        });

        it('formats centiseconds as seconds with two decimals', () => {
            expect(cs_to_s(0)).toBe('0.00');
            expect(cs_to_s(7)).toBe('0.07');
            expect(cs_to_s(1234)).toBe('12.34');
        });
    });

    describe('deepCopy', () => {
        it('deep copies plain objects and arrays without sharing nested references', () => {
            const source: {
                id: number;
                nested: {
                    values: [number, { label: string }];
                };
            } = {
                id: 1,
                nested: {
                    values: [1, { label: 'one' }],
                },
            };

            const copy = deepCopy(source);
            copy.nested.values[1].label = 'changed';

            expect(copy).toEqual({
                id: 1,
                nested: {
                    values: [1, { label: 'changed' }],
                },
            });
            expect(source.nested.values[1].label).toBe('one');
            expect(copy.nested).not.toBe(source.nested);
            expect(copy.nested.values).not.toBe(source.nested.values);
        });

        it('returns primitives and null directly', () => {
            expect(deepCopy(1)).toBe(1);
            expect(deepCopy('text')).toBe('text');
            expect(deepCopy(null)).toBeNull();
        });
    });

    describe('sleep', () => {
        it('resolves with the requested milliseconds after the timeout', async () => {
            vi.useFakeTimers();

            const promise = sleep(25);
            const onResolve = vi.fn();
            void promise.then(onResolve);

            await vi.advanceTimersByTimeAsync(24);
            expect(onResolve).not.toHaveBeenCalled();

            await vi.advanceTimersByTimeAsync(1);
            await expect(promise).resolves.toBe(25);
            expect(onResolve).toHaveBeenCalledWith(25);
        });
    });
});
