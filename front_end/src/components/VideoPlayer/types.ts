import type { AnyVideo } from '@/utils/fileIO';

export const videoNumericParamKeys = [
    'bbbv',
    'bbbv_s',
    'bbbv_solved',
    'ce',
    'ce_s',
    'cell0',
    'cell1',
    'cell2',
    'cell3',
    'cell4',
    'cell5',
    'cell6',
    'cell7',
    'cell8',
    'cl',
    'cl_s',
    'column',
    'corr',
    'current_event_id',
    'dce',
    'double',
    'double_s',
    'etime',
    'flag',
    'flag_s',
    'game_board_state',
    'hzini',
    'ioe',
    'isl',
    'lce',
    'left',
    'left_s',
    'level',
    'mine_num',
    'mode',
    'mouse_state',
    'op',
    'path',
    'pix_size',
    'pluck',
    'rce',
    'right',
    'right_s',
    'row',
    'rqp',
    'rtime',
    'rtime_ms',
    'stnb',
    'thrp',
    'video_end_time',
    'video_start_time',
    'zini',
] as const satisfies readonly (keyof AnyVideo)[];

export type VideoNumericParamKey = typeof videoNumericParamKeys[number];

export type CustomCounterTableRow = [label: string, expression: string];

export interface CustomCounterConfig {
    table: CustomCounterTableRow[];
    thWidth: number;
    tdWidth: number;
    fontSize: number;
}

export const defaultCustomCounterTable: CustomCounterTableRow[] = [
    ['time', 'roundTo(bbbv_solved / bbbv_s, 3) || "@" || roundTo(etime, 3) || "/" || roundTo(rtime, 3)'],
    ['bvs', 'bbbv_solved || "/" || bbbv || "~" || roundTo(bbbv_s, 3)'],
    ['ce', 'ce || "@" || roundTo(ce_s,3)'],
    ['cl', 'cl || "@" || roundTo(cl_s,3)'],
    ['stnb', 'roundTo(stnb, 3)'],
    ['opis', 'op || "op " || isl || "is"'],
    ['ioe', 'roundTo(corr, 3) || "*" || roundTo(thrp, 3) || "=" || roundTo(ioe, 3)'],
    ['mov', 'roundTo(path / 16, 3) || "@" || roundTo(path / 16 / bbbv_solved * bbbv_s, 3)'],
    ['cell0-2', 'cell0 || "/" || cell1 || "/" || cell2'],
    ['cell3-5', 'cell3 || "/" || cell4 || "/" || cell5'],
    ['cell6-8', 'cell6 || "/" || cell7 || "/" || cell8'],
];

export function cloneCustomCounterTable(config: CustomCounterTableRow[]): CustomCounterTableRow[] {
    return config.map(([label, expression]) => [label, expression]);
}

export function isCustomCounterTable(value: unknown): value is CustomCounterTableRow[] {
    return Array.isArray(value) && value.every((row) => isCustomCounterTableRow(row));
}

export function isCustomCounterTableRow(value: unknown): value is CustomCounterTableRow {
    return Array.isArray(value)
        && value.length === 2
        && typeof value[0] === 'string'
        && typeof value[1] === 'string';
}
