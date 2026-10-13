import { Parser } from 'expr-eval';
import { describe, expect, it, vi } from 'vitest';

import { counterVariables, defaultCounterConfig, displayCounter, prepareCounter } from './counter';
import type { CounterEvent, CounterValues } from './counter';
import { createDifferenceEvaluator } from './counterDifference';

function events(): CounterEvent[] {
    return [1, 3, 8, 16].map((value, index) => ({ timeMs: index * 1000,
        eventIndex: index,
        button: true,
        boardChanged: true,
        values: { ...Object.fromEntries(counterVariables.map((key) => [key, value])) as CounterValues, time: index, bbbv: 99 } }));
}

function prepare(expression: string, snapshots = events()) {
    return prepareCounter({ ...defaultCounterConfig().rows[0], expression, samplingMode: 'button' }, snapshots);
}

describe('counter differences', () => {
    it('evaluates the default rates over 1000 continuous samples, including non-button events', () => {
        const snapshots: CounterEvent[] = [0, 1, 2].map((index) => ({ timeMs: index * 1000,
            eventIndex: index,
            button: false,
            boardChanged: false,
            values: { ...Object.fromEntries(counterVariables.map((key) => [key, 0])) as CounterValues, time: index, bbbv_solved: [0, 4, 12][index], lce: [0, 2, 5][index], rce: [0, 3, 6][index], dce: [0, 1, 4][index], path: [0, 32, 80][index] } }));
        const original = structuredClone(snapshots);
        const { rows } = defaultCounterConfig();
        expect(rows.map((row) => row.key)).toEqual(['Bvs', 'Ces', 'Mov']);
        for (const [index, row] of rows.entries()) {
            const result = prepareCounter(row, snapshots, 2000);
            expect(result.error).toBe('');
            expect(result.samples).toHaveLength(2001);
            expect(result.samples.slice(0, 1000).every((sample) => Number.isNaN(sample.value))).toBe(true);
            expect(result.samples[1000].value).toBe([4, 6, 2][index]);
            expect(result.samples[2000].value).toBe([8, 9, 3][index]);
        }
        expect(snapshots).toEqual(original);
    });

    it('differences fields and compound expressions without changing source snapshots', () => {
        const snapshots = events();
        const original = structuredClone(snapshots);
        for (const [expression, expected] of [
            ['d(time)', [NaN, 1, 1, 1]],
            ['d(left + right + double)', [NaN, 6, 15, 24]],
            ['d((left + right + double)^2)', [NaN, 72, 495, 1728]],
            ['d(left) + d(right * 2)', [NaN, 6, 15, 24]],
            ['d(bbbv)', [NaN, 0, 0, 0]],
        ] as const) {
            const result = prepare(expression, snapshots);
            expect(result.error).toBe('');
            expect(result.samples.map((sample) => sample.value)).toEqual(expected);
        }
        expect(snapshots).toEqual(original);
    });

    it('supports nested differences at multiple orders', () => {
        expect(prepare('d(d(left))').samples.map((sample) => sample.value)).toEqual([NaN, NaN, 3, 3]);
        expect(prepare('d(d(d(left)))').samples.map((sample) => sample.value)).toEqual([NaN, NaN, NaN, 0]);
        expect(prepare('d(d(left) / d(time))').samples.map((sample) => sample.value)).toEqual([NaN, NaN, 3, 3]);
    });

    it('supports sample-count steps with the default step remaining one', () => {
        for (const [expression, expected] of [
            ['d(left, 1)', [NaN, 2, 5, 8]],
            ['d(left, 2)', [NaN, NaN, 7, 13]],
            ['d(left + right, max(1, 2)) / d(time, 2)', [NaN, NaN, 7, 13]],
            ['d(left, 4)', [NaN, NaN, NaN, NaN]],
            ['d(left, time > 1 ? 2 : 1)', [NaN, 2, 7, 13]],
        ] as const) {
            const result = prepare(expression);
            expect(result.error).toBe('');
            expect(result.samples.map((sample) => sample.value)).toEqual(expected);
        }
    });

    it('combines nested steps and preserves lazy branches', () => {
        const snapshots = Array.from({ length: 7 }, (_, index) => ({ ...events()[0], timeMs: index * 1000, eventIndex: index, values: { ...events()[0].values, left: index ** 2 } }));
        expect(prepare('d(d(left, 2), 3)', snapshots).samples.map((sample) => sample.value)).toEqual([NaN, NaN, NaN, NaN, NaN, 12, 12]);
        expect(prepare('time < 0 ? d(left, 0) : d(left, 2)').error).toBe('');
        expect(prepare('d(left, 2) ? 1 : 0').samples.map((sample) => sample.value)).toEqual([0, 0, 1, 1]);
    });

    it('differences library functions, arrays, strings, conditional parameters and statements using the existing grammar', () => {
        for (const [expression, expected] of [
            ['d(roundTo(left / max(time, 1), 2))', [NaN, 2, 1, 1.33]],
            ['d(time > 1 ? [left, right][0] : length("d(time)"))', [NaN, 0, 1, 8]],
            ['d((left; right))', [NaN, 2, 5, 8]],
            ['d(time > 1 ? left : right * 2)', [NaN, 4, 2, 8]],
        ] as const) {
            const result = prepare(expression);
            expect(result.error).toBe('');
            for (const [index, value] of expected.entries()) {
                if (Number.isNaN(value)) expect(result.samples[index].value).toBeNaN();
                else expect(result.samples[index].value).toBeCloseTo(value);
            }
        }
    });

    it('uses the actual previous sample even when a conditional skipped the previous difference call', () => {
        const result = prepare('time == 1 ? d(left) : d(right * 2)');
        expect(result.error).toBe('');
        expect(result.samples.map((sample) => sample.value)).toEqual([NaN, 2, 10, 16]);
        expect(prepare('time < 0 ? d(left[0]) : d(left)').error).toBe('');
    });

    it('resolves differences used as conditions and short-circuit logical operands', () => {
        const snapshots = events();
        snapshots[2].values.left = snapshots[1].values.left;
        for (const expression of ['d(left) ? 1 : 2', '(d(left) and time > 0) ? 1 : 2', '(d(left) or 0) ? 1 : 2']) {
            const result = prepare(expression, snapshots);
            expect(result.error).toBe('');
            expect(result.samples.map((sample) => sample.value)).toEqual([2, 1, 2, 1]);
        }
        expect(prepare('(0 and d(left[0])) ? 1 : 2').samples.map((sample) => sample.value)).toEqual([2, 2, 2, 2]);
    });

    it('chooses predecessors after mode filtering and keeping the last eligible event in each millisecond', () => {
        const snapshots = [
            { ...events()[0], timeMs: 0, button: false, boardChanged: false },
            { ...events()[1], timeMs: 1 },
            { ...events()[2], timeMs: 1, button: false },
            { ...events()[3], timeMs: 1, button: false, boardChanged: false },
            { ...events()[1], timeMs: 2, boardChanged: false },
            { ...events()[2], timeMs: 2, button: false },
            { ...events()[3], timeMs: 10 },
        ];
        for (const [samplingMode, adjacent, stepped] of [['continuous', [NaN, 15, -8, 0, 0, 0, 0, 0, 0, 0, 8], [NaN, NaN, 7, -8, 0, 0, 0, 0, 0, 0, 8]], ['button', [NaN, 0, 13], [NaN, NaN, 13]], ['board', [NaN, 0, 8], [NaN, NaN, 8]]] as const) {
            for (const [expression, expected] of [['d(left)', adjacent], ['d(left, 2)', stepped]] as const) {
                const result = prepareCounter({ ...defaultCounterConfig().rows[0], expression, samplingMode }, snapshots);
                expect(result.error).toBe('');
                expect(result.samples.map((sample) => sample.value)).toEqual(expected);
            }
        }
    });

    it('retains nonfinite differences and interpolates computed results rather than differencing interpolated fields', () => {
        const result = prepare('d(left) / d(time)');
        expect(displayCounter(result, 0)).toEqual({ value: 'NaN', error: false });
        expect(displayCounter(result, 1500)).toEqual({ value: '3.500', error: false });
        expect(displayCounter(result, 4000)).toEqual({ value: '8.000', error: false });
        const snapshots = events();
        for (const [index, value] of [2, Infinity, -Infinity, NaN].entries()) snapshots[index].values.left = value;
        expect(prepare('d(left)', snapshots).samples.map((sample) => sample.value)).toEqual([NaN, Infinity, -Infinity, NaN]);
        expect(prepare('d(left)', [snapshots[1], snapshots[1]]).samples.map((sample) => sample.value)).toEqual([NaN]);
    });

    it.each(['d()', 'd(left, 1, 2)'])('reports wrong arity for %s', (expression) => {
        expect(displayCounter(prepare(expression), 1000)).toEqual({ value: 'd expects one expression and an optional sample step', error: true });
    });

    it.each(['0', '-1', '1.5', '0 / 0', '1 / 0', '-1 / 0', '"2"', '[2]', 'left > 0'])('rejects invalid sample step %s', (step) => {
        expect(displayCounter(prepare(`d(left, ${step})`), 1000)).toEqual({ value: 'd expects a positive integer sample step', error: true });
    });

    it.each(['d("2")', 'd([left])', 'd(left > 0)', 'd(roundTo)'])('rejects a nonnumeric difference operand %s', (expression) => {
        expect(displayCounter(prepare(expression), 1000)).toEqual({ value: 'd expects a numeric expression', error: true });
    });

    it('retains variable and assignment restrictions inside differences', () => {
        expect(prepare('d(unknown)').error).toBe('Unknown variable: unknown');
        expect(prepare('d(left = 3)').error).not.toBe('');
        expect(prepare('d(left +)').error).not.toBe('');
        expect(prepare('__counterDifference0').error).toBe('Unknown variable: __counterDifference0');
    });

    it('evaluates by index independently of evaluation order and caches operands without changing the parsed expression', () => {
        const parser = new Parser();
        const probe = vi.fn((value: number) => value);
        (parser.functions as Record<string, (value: number) => number>).probe = probe;
        const expression = parser.parse('d(d(probe(left)))');
        const evaluate = createDifferenceEvaluator(parser, expression, events().map((snapshot) => snapshot.values));
        expect([3, 1, 2, 0, 3].map(evaluate)).toEqual([3, NaN, 3, NaN, 3]);
        expect(probe).toHaveBeenCalledTimes(4);
        probe.mockClear();
        const stepped = createDifferenceEvaluator(parser, parser.parse('d(d(probe(left), 2), 1)'), events().map((snapshot) => snapshot.values));
        expect([3, 1, 2, 0, 3].map(stepped)).toEqual([6, NaN, NaN, NaN, 6]);
        expect(probe).toHaveBeenCalledTimes(4);
        expect(expression.variables()).toEqual(['d', 'left']);
        expect((): unknown => expression.evaluate({ left: 3 })).toThrow('undefined variable: d');
    });
});
