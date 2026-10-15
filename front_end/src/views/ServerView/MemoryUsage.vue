<template>
    <MemoryDonut data-memory-chart="process" :title="t('local.title')" :series="series" :total="lastGood?.total_bytes ?? null" :sampled-at="lastGood?.sampled_at" :loading="loading" :failed="failed" :reason="section?.reason" @refresh="emit('refresh')">
        <p v-if="lastGood" class="memory-description" :title="t('local.scope')">
            {{ t(`local.${lastGood.metric}`) }}
        </p>
        <p v-if="lastGood?.host" class="memory-description">
            {{ t('local.hostTotal') }}: {{ formatBytes(lastGood.host.total_bytes) }} · {{ t('local.available') }}: {{ formatBytes(lastGood.host.available_bytes) }}
        </p>
    </MemoryDonut>
</template>

<script setup lang="ts">
import type { PropType } from 'vue';
import { computed, shallowRef, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import type { ProcessMemorySection } from './memory';
import { memoryColors, processMemoryGroups } from './memory';
import MemoryDonut from './MemoryDonut.vue';

import { formatBytes } from '@/utils/strings';

const props = defineProps({
    section: { type: Object as PropType<ProcessMemorySection | null>, default: null },
    loading: { type: Boolean, default: false },
    failed: { type: Boolean, default: false },
});
const emit = defineEmits<{ refresh: [] }>();
const lastGood = shallowRef<ProcessMemorySection | null>(null);
watch(() => props.section, (section) => {
    if (section?.status === 'ready' && section.groups && section.total_bytes !== null && section.sampled_at) lastGood.value = section;
}, { immediate: true });
const series = computed(() => {
    const groups = lastGood.value?.groups;
    return groups ? processMemoryGroups.map((key, index) => ({ key, name: t(`local.${key}`), value: groups[key], color: memoryColors[index] })) : [];
});

const i18nMessages = {
    'zh-cn': { local: {
        title: '内存占用',
        uwsgi: 'uWSGI',
        apscheduler: 'APScheduler',
        redis: 'Redis',
        mysql: 'MySQL',
        db_worker: 'db_worker',
        other: '其他',
        pss: '进程驻留内存（PSS）',
        rss: '进程驻留内存（RSS，共享内存可能重复计算）',
        scope: '合计为进程内存，不包含内核和未映射的文件缓存。',
        hostTotal: '主机总内存',
        available: '可用内存',
    } },
    en: { local: {
        title: 'Memory Usage',
        uwsgi: 'uWSGI',
        apscheduler: 'APScheduler',
        redis: 'Redis',
        mysql: 'MySQL',
        db_worker: 'db_worker',
        other: 'Other',
        pss: 'Resident process memory (PSS)',
        rss: 'Resident process memory (RSS; shared pages may be counted more than once)',
        scope: 'The total covers processes, excluding kernel memory and unmapped file cache.',
        hostTotal: 'Host memory',
        available: 'Available memory',
    } },
};
const { t } = useI18n({ messages: i18nMessages });
</script>

<style scoped>
.memory-description {
    margin: 4px 0;
    font-size: var(--ui-font-size-small);
    overflow-wrap: anywhere;
}
</style>
