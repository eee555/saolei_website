import { useLocalStorage } from '@vueuse/core';

import {
    cloneCustomCounterTable,
    defaultCustomCounterTable,
} from './types';
import type { CustomCounterConfig } from './types';

export const customCounterConfig = useLocalStorage<CustomCounterConfig>(
    'custom-counter-config',
    {
        table: cloneCustomCounterTable(defaultCustomCounterTable),
        thWidth: 90,
        tdWidth: 130,
        fontSize: 12,
    },
);
