import { readFileSync } from 'node:fs';

import { describe, expect, it } from 'vitest';

import { ArbiterCsvError, parseArbiterCsv } from './arbiterCsv';

const sample = readFileSync(new URL('../../../cypress/fixtures/stats_csv.csv', import.meta.url), 'utf8');
const header = 'Day,Month,Year,Hour,Min,Sec,Time';
const row = '5,10,2023,21,25,57,35.09';

describe('Arbiter CSV input', () => {
    it('reads the real fixture without losing millisecond precision or click totals', () => {
        const { records, issues } = parseArbiterCsv(sample);
        expect(issues).toEqual([]);
        expect(records).toHaveLength(1);
        expect(records[0].video).toMatchObject({ level: 'e', timems: 35090, bv: 132, cl: 158, ce: 137, right_ce: 20, path: 5960 });
        expect(records[0].video.end_time.toISOString()).toBe('2023-10-05T21:25:57.000Z');
        expect(records[0].stats.cell0).toBe(90);
    });

    it.each([['BEG', 'b'], ['INT', 'i']])('maps %s to %s', (mode, level) => {
        expect(parseArbiterCsv(`${header},mode\n${row},${mode}`).records[0].video.level).toBe(level);
    });

    it('handles quoted fields and source lines, deduplicating identity despite different stats', () => {
        const result = parseArbiterCsv(`\uFEFF${header},BBBV,Note\r\n${row},132,"comma, and\nnewline"\r\n\r\n${row},133,duplicate\r\n`);
        expect(result.records).toHaveLength(1);
        expect(result.issues).toContainEqual({ code: 'duplicate', row: 5 });
        expect(result.issues).toContainEqual({ code: 'mismatch', row: 5 });
    });

    it('rejects file structure errors and oversized input', () => {
        for (const input of [`${header},Day\n${row},5`, 'Day,Time\n5,35.09', `${header}\n"5,10`, ' '.repeat(10 * 1024 * 1024 + 1)]) {
            expect(() => parseArbiterCsv(input)).toThrow(ArbiterCsvError);
        }
        expect(() => parseArbiterCsv(`${header}\n${`${row}\n`.repeat(100001)}`)).toThrow(ArbiterCsvError);
    });

    it('excludes invalid identities, but keeps rows with missing or invalid auxiliary stats', () => {
        const result = parseArbiterCsv(`${header},BBBV,mode\n31,2,2023,21,25,57,35.09,132,EXP\n5,10,2023,21,25,57,,132,EXP\n${row},bad,OTHER\n6,10,2023,21,25,57,0.009`);
        expect(result.records).toHaveLength(2);
        expect(result.records[1].video.timems).toBe(9);
        expect(result.records[0].video.bv).toBeNaN();
        expect(result.issues.map((issue) => issue.code)).toEqual(expect.arrayContaining(['date', 'time', 'number', 'level', 'columns']));
        expect(parseArbiterCsv(`${header}\n${row},extra`).records).toHaveLength(1);
        expect(parseArbiterCsv(`${header}\n5,10,2023,21,25,57,35.0901`).records).toHaveLength(0);
    });
});
