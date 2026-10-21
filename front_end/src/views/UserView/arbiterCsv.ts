import Papa from 'papaparse';

import type { VideoAbstractData } from '@/utils/videoabstract';

export const MAX_CSV_BYTES = 10 * 1024 * 1024;
export const MAX_CSV_ROWS = 100000;
const dateColumns = ['Year', 'Month', 'Day', 'Hour', 'Min', 'Sec'] as const;
const requiredColumns = [...dateColumns, 'Time'];
const levels: Record<string, string> = { BEG: 'b', INT: 'i', EXP: 'e' };
const numericColumns = ['BBBV', 'Lcl', 'Rcl', 'Dcl', 'Leff', 'Reff', 'Deff', 'Openings', 'Islands', 'Path', 'GZiNi', 'HZiNi', ...Array.from({ length: 9 }, (_, i) => `cell${i}`)];

export interface CsvIssue {
    code: 'headers' | 'quotes' | 'limit' | 'date' | 'time' | 'columns' | 'number' | 'level' | 'duplicate' | 'mismatch' | 'missingEndTime' | 'read';
    row?: number;
    field?: string;
}
export interface ArbiterCsvRecord {
    key: string;
    row: number;
    video: VideoAbstractData & { end_time: Date };
    stats: Record<string, number>;
}
export interface ArbiterCsvResult {
    records: ArbiterCsvRecord[];
    issues: CsvIssue[];
}
export class ArbiterCsvError extends Error {
    public readonly issue: CsvIssue;

    public constructor(issue: CsvIssue) {
        super(issue.code);
        this.issue = issue;
    }
}

export function videoMatchKey(endTime: Date | undefined, timems: number): string | undefined {
    if (!endTime || !Number.isFinite(endTime.getTime()) || !Number.isSafeInteger(timems) || timems < 0) return undefined;
    return `${Math.floor(endTime.getTime() / 1000)}:${timems}`;
}

function parseMilliseconds(value: string): number | undefined {
    if (!(/^\d+(?:\.\d{1,3}0*)?$/).test(value)) return undefined;
    const [seconds, fraction = ''] = value.split('.');
    const result = Number(seconds) * 1000 + Number(fraction.padEnd(3, '0').slice(0, 3));
    return Number.isSafeInteger(result) ? result : undefined;
}

export function parseArbiterCsv(text: string): ArbiterCsvResult {
    if (new TextEncoder().encode(text).byteLength > MAX_CSV_BYTES) throw new ArbiterCsvError({ code: 'limit' });
    // Keep header cells and empty rows so duplicate headers cannot be silently renamed,
    // and source line numbers remain available. Papa handles quoting and line endings.
    const parsed = Papa.parse<string[]>(text.replace(/^\uFEFF/, ''), { delimiter: ',', dynamicTyping: false, preview: MAX_CSV_ROWS + 2 });
    if (parsed.errors.some((error) => error.type === 'Quotes')) throw new ArbiterCsvError({ code: 'quotes' });
    if (parsed.meta.truncated) throw new ArbiterCsvError({ code: 'limit' });
    const headers = parsed.data[0]?.map((cell) => cell.trim()) ?? [];
    if (new Set(headers).size !== headers.length || requiredColumns.some((column) => !headers.includes(column))) throw new ArbiterCsvError({ code: 'headers' });
    const records = new Map<string, ArbiterCsvRecord>();
    const issues: CsvIssue[] = [];
    let sourceLine = 1;
    let rowCount = 0;
    for (const cells of parsed.data) {
        const row = sourceLine;
        sourceLine += 1 + cells.reduce((count, cell) => count + (cell.match(/\r\n|\r|\n/g)?.length ?? 0), 0);
        if (row === 1 || cells.every((cell) => cell.trim() === '')) continue;
        if (++rowCount > MAX_CSV_ROWS) throw new ArbiterCsvError({ code: 'limit' });
        const values = Object.fromEntries(headers.map((header, index) => [header, cells[index]?.trim() ?? '']));
        if (cells.length !== headers.length) issues.push({ code: 'columns', row });
        const parts = dateColumns.map((column) => ((/^\d+$/).test(values[column]) ? Number(values[column]) : NaN));
        const [year, month, day, hour, minute, second] = parts;
        const end = new Date(Date.UTC(year, month - 1, day, hour, minute, second));
        const roundTrip = [end.getUTCFullYear(), end.getUTCMonth() + 1, end.getUTCDate(), end.getUTCHours(), end.getUTCMinutes(), end.getUTCSeconds()];
        if (year < 100 || !parts.every((part, index) => Number.isSafeInteger(part) && part === roundTrip[index])) {
            issues.push({ code: 'date', row });
            continue;
        }
        const timems = parseMilliseconds(values.Time);
        if (timems === undefined) {
            issues.push({ code: 'time', row });
            continue;
        }
        const stats: Record<string, number> = {};
        for (const column of numericColumns) {
            const raw = values[column];
            if (!raw) continue;
            const number = Number(raw);
            if (!(/^\d+(?:\.\d+)?$/).test(raw) || !Number.isFinite(number) || number < 0 || (column !== 'Path' && !Number.isSafeInteger(number))) issues.push({ code: 'number', row, field: column });
            else stats[column] = number;
        }
        const level = levels[values.mode];
        if (!level) issues.push({ code: 'level', row, field: values.mode || '—' });
        const sum = (columns: string[]) => (columns.every((column) => stats[column] !== undefined) ? columns.reduce((total, column) => total + stats[column], 0) : undefined);
        const key = `${Math.floor(end.getTime() / 1000)}:${timems}`;
        const record: ArbiterCsvRecord = { key,
            row,
            stats,
            video: {
                end_time: end,
                timems,
                level: level ?? 'unknown',
                software: 'a',
                mode: '00',
                bv: stats.BBBV ?? NaN,
                cl: sum(['Lcl', 'Rcl', 'Dcl']),
                ce: sum(['Leff', 'Reff', 'Deff']),
                right_ce: stats.Reff,
                path: stats.Path,
            } };
        const previous = records.get(key);
        if (previous) {
            issues.push({ code: 'duplicate', row });
            if (JSON.stringify(previous.stats) !== JSON.stringify(stats) || previous.video.level !== record.video.level) issues.push({ code: 'mismatch', row });
        } else records.set(key, record);
    }
    return { records: [...records.values()], issues };
}
