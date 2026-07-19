import { useLocalStorage } from '@vueuse/core';
import type { Ref } from 'vue';

import { cloneCustomCounterConfig, defaultCustomCounterConfig, isCustomCounterConfig } from './types';
import type { CustomCounterConfig } from './types';

const storedCustomCounterConfig = useLocalStorage<unknown>(
    'custom-counter-config',
    cloneCustomCounterConfig(defaultCustomCounterConfig),
);

if (!isCustomCounterConfig(storedCustomCounterConfig.value)) {
    storedCustomCounterConfig.value = cloneCustomCounterConfig(defaultCustomCounterConfig);
}

export const customCounterConfig = storedCustomCounterConfig as Ref<CustomCounterConfig>;
