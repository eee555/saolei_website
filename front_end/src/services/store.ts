import { useLocalStorage } from '@vueuse/core';

export const serviceConfig = useLocalStorage(
    'service-config',
    {
        userInfoUpdateInterval: 86400000,
        userInfoLastUpdate: 0,
        userInfoBatchDelay: 500,
        userInfoBatchSize: 100,
        videoInfoBatchSize: 100,
        videoInfoBatchDelay: 250,
        videoInfoCacheUnpublished: false,
    },
    { mergeDefaults: true },
);
