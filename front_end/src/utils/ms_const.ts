import { useLocalStorage } from '@vueuse/core';

export const MS_Levels = ['b', 'i', 'e'] as const;
export type MS_Level = typeof MS_Levels[number];

export const MS_Softwares = ['e', 'a', 'r', 'm', 'u'] as const;
export type MS_Software = typeof MS_Softwares[number];

export const STNB_const = useLocalStorage('stnb_const', {
    b: 47.299,
    i: 153.73,
    e: 435.001,
});

export enum MS_State {
    Plain = 'a',
    Frozen = 'b',
    Official = 'c',
    Identifier = 'd',
    External = 'e',
}

export enum TournamentState {
    Pending = 'p',
    Ongoing = 'o',
    Finished = 'f',
    Preparing = 'r',
    Cancelled = 'c',
    Awarded = 'a',
}

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
