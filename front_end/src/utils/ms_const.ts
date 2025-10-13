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
