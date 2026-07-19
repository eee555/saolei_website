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

export type CustomCounterConfigRow = [label: string, expression: string];

export type CustomCounterConfig = CustomCounterConfigRow[];

export const defaultCustomCounterConfig: CustomCounterConfig = [
    ['time', 'roundTo(rtime, 3) || "/" || roundTo(etime, 3)'],
    ['bvs', 'roundTo(bbbv_s, 3) || "@" || bbbv_solved || "/" || bbbv'],
    ['cl', 'cl || "=" || left || "+" || right || "+" || double'],
    ['cls', 'roundTo(cl_s, 3) || "=" || roundTo(left_s, 3) || "+" || roundTo(right_s, 3) || "+" || roundTo(double_s, 3)'],
    ['ce', 'ce || "=" || lce || "+" || rce || "+" || dce'],
    ['cell0-2', 'cell0 || "/" || cell1 || "/" || cell2'],
    ['cell3-5', 'cell3 || "/" || cell4 || "/" || cell5'],
    ['cell6-8', 'cell6 || "/" || cell7 || "/" || cell8'],
    ['column', 'column'],
    ['corr', 'corr'],
    ['current_event_id', 'current_event_id'],
    ['flag', 'flag'],
    ['flag_s', 'flag_s'],
    ['game_board_state', 'game_board_state'],
    ['hzini', 'hzini'],
    ['ioe', 'ioe'],
    ['isl', 'isl'],
    ['level', 'level'],
    ['mine_num', 'mine_num'],
    ['mode', 'mode'],
    ['mouse_state', 'mouse_state'],
    ['op', 'op'],
    ['path', 'path'],
    ['pix_size', 'pix_size'],
    ['pluck', 'pluck'],
    ['row', 'row'],
    ['rqp', 'rqp'],
    ['rtime_ms', 'rtime_ms'],
    ['stnb', 'stnb'],
    ['thrp', 'thrp'],
    ['video_end_time', 'video_end_time'],
    ['video_start_time', 'video_start_time'],
    ['zini', 'zini'],
];

export function cloneCustomCounterConfig(config: CustomCounterConfig): CustomCounterConfig {
    return config.map(([label, expression]) => [label, expression]);
}

export function isCustomCounterConfig(value: unknown): value is CustomCounterConfig {
    return Array.isArray(value) && value.every((row) => isCustomCounterConfigRow(row));
}

export function isCustomCounterConfigRow(value: unknown): value is CustomCounterConfigRow {
    return Array.isArray(value)
        && value.length === 2
        && typeof value[0] === 'string'
        && typeof value[1] === 'string';
}
