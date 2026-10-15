import type { PropType } from 'vue';
import { defineComponent, h } from 'vue';
import type { VueUiDonutConfig, VueUiDonutDatasetItem } from 'vue-data-ui';

import type { MemoryUsageResponse } from './memory';

export function memoryResponse(): MemoryUsageResponse {
    return {
        memory: {
            status: 'ready',
            reason: null,
            sampled_at: '2026-10-15T12:00:00Z',
            metric: 'pss',
            total_bytes: 3072,
            groups: { uwsgi: 1024, apscheduler: 512, redis: 256, mysql: 512, db_worker: 256, other: 512 },
            host: { total_bytes: 8192, available_bytes: 2048 },
            unreadable_processes: 0,
        },
        redis: {
            status: 'ready',
            reason: null,
            sampled_at: '2026-10-15T12:00:01Z',
            metric: 'redis_allocated',
            total_bytes: 1024,
            groups: { pb_rankings: 512, other_rankings: 256, latest_videos: 128, other: 128 },
            estimated: true,
            samples: 5,
        },
    };
}

export const DonutStub = defineComponent({
    props: {
        config: { type: Object as PropType<VueUiDonutConfig>, required: true },
        dataset: { type: Array as PropType<VueUiDonutDatasetItem[]>, required: true },
    },
    setup: (props) => () => h('div', {
        'data-cy': 'memory-donut',
        'data-theme': props.config.theme,
        'data-series': JSON.stringify(props.dataset),
    }),
});
