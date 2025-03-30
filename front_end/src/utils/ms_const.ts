import { useLocalStorage } from "@vueuse/core";

export const MS_Levels = ['b', 'i', 'e'] as const;
export type MS_Level = typeof MS_Levels[number];

export const MS_Softwares = ['e', 'a', 'r', 'm', 'u'] as const;
export type MS_Software = typeof MS_Softwares[number];

export const STNB_const = useLocalStorage('stnb_const', {
    b: 47.299,
    i: 153.73,
    e: 435.001,
})
