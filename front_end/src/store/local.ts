import { useLocalStorage } from '@vueuse/core';

const localDefaultSettings = {
    darkmode: matchMedia('(prefers-color-scheme: dark)').matches,
    experimental: false,
    colored: false,
    language: navigator.language.toLocaleLowerCase(),
    navigation_layout: 'top' as 'top' | 'sidebar',
    notification_duration: 4500,
    tooltip_show: true,
    vienna_logo_legacy: false,
    autoUploadAfterParse: false,
    autoRemoveAfterUpload: false,
    nameFormat: 'first-last' as 'first-last' | 'last-first',
};

export type LocalSettings = typeof localDefaultSettings;
export const local = useLocalStorage('local', localDefaultSettings, { mergeDefaults: true });
