import { useLocalStorage } from '@vueuse/core';

export const serviceConfig = useLocalStorage(
    'service-config',
    {
        userInfoUpdateInterval: 86400000,
        userInfoLastUpdate: 0,
        userInfoPollRate: 500,
        userInfoRequestTimeout: 10000,
        userInfoBulkSize: 100,
    },
    { mergeDefaults: true },
);
