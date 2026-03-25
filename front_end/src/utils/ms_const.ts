import { useLocalStorage } from '@vueuse/core';

export type EnumMap<T extends string | number | symbol, V> = { [K in T]: V; };

/**
 * 根据键数组和默认值，创建一个包含所有键且值均为默认值的对象。
 * 返回类型精确到键的联合类型，确保所有键都存在。
 */
export function createEnumMap<T extends readonly string[], V>(
    keys: T,
    defaultValue: V,
): { [K in T[number]]: V } {
    return Object.fromEntries(keys.map((key) => [key, defaultValue])) as {
        [K in T[number]]: V;
    };
}

export const MS_Levels = ['b', 'i', 'e'] as const;
export type MS_Level = typeof MS_Levels[number];

export const MS_Softwares = ['e', 'a', 'r', 'm'] as const;
export type MS_Software = typeof MS_Softwares[number];

export const STNB_const = useLocalStorage('stnb_const', {
    b: 47.299,
    i: 153.73,
    e: 435.001,
});

export const MS_Mode = {
    Standard: '00',
    SpeedNG: '05',
    HardcoreNG: '06',
    Recursive: '11',
    NoFlag: '12',
} as const;
export type MS_Mode = typeof MS_Mode[keyof typeof MS_Mode];

export const MS_State = {
    Plain: 'a',
    Frozen: 'b',
    Official: 'c',
    Identifier: 'd',
} as const;
export type MS_State = typeof MS_State[keyof typeof MS_State];

export const TournamentState = {
    Pending: 'p',
    Ongoing: 'o',
    Finished: 'f',
    Preparing: 'r',
    Cancelled: 'c',
    Awarded: 'a',
} as const;
export type TournamentState = typeof TournamentState[keyof typeof TournamentState];

export enum TournamentSeries {
    General = 'a',
    GSC = 'g',
    Unknown = 'u',
}

export const GSCDefaults = {
    bt: 10000,
    it: 60000,
    et: 240000,
} as const;

export const ColorTemplateNames = ['time', 'bvs', 'stnb', 'ioe', 'thrp', 'path', 'custom'] as const;
export type ColorTemplateName = typeof ColorTemplateNames[number];

export const ColumnChoices = ['state', 'upload_time', 'end_time', 'player', 'software', 'mode', 'level', 'time', 'bv', 'bvs', 'stnb', 'ces', 'cls', 'corr', 'ioe', 'thrp', 'path', 'file_size'] as const;
export type ColumnChoice = typeof ColumnChoices[number];
