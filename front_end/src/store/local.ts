import { useLocalStorage } from '@vueuse/core';

const localDefaultSettings = {
    darkmode: matchMedia('(prefers-color-scheme: dark)').matches,
    experimental: false,
    language: navigator.language.toLocaleLowerCase(),
    language_show: true,
    menu_font_size: 18,
    menu_height: 60,
    menu_icon: false,
    notification_duration: 4500,
    tooltip_show: true,
    vienna_logo_legacy: false,
    autoUploadAfterParse: false,
    autoRemoveAfterUpload: false,
    nameFormat: 'first-last' as 'first-last' | 'last-first',
};

export type LocalSettings = typeof localDefaultSettings;
export const local = useLocalStorage('local', localDefaultSettings, { mergeDefaults: true });
