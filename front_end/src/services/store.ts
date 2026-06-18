import { useLocalStorage } from '@vueuse/core';

export const serviceConfig = useLocalStorage(
    'service-config',
    {
        userInfoUpdateInterval: 86400000,
        userInfoLastUpdate: 0,
        userInfoBatchDelay: 500,
        userInfoBatchSize: 100,
    },
    { mergeDefaults: true },
);
