<template>
    <MemoryDonut data-memory-chart="redis" :title="t('local.title')" :series="series" :total="lastGood?.total_bytes ?? null" :sampled-at="lastGood?.sampled_at" :loading="loading" :failed="failed" :reason="section?.reason" @refresh="emit('refresh')">
        <p v-if="lastGood" class="memory-description" :title="t('local.explanation')">
            {{ t('local.estimated') }}
        </p>
    </MemoryDonut>
</template>

<script setup lang="ts">
import type { PropType } from 'vue';
import { computed, shallowRef, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import type { RedisMemorySection } from './memory';
import { memoryColors, redisMemoryGroups } from './memory';
import MemoryDonut from './MemoryDonut.vue';

const props = defineProps({
    section: { type: Object as PropType<RedisMemorySection | null>, default: null },
    loading: { type: Boolean, default: false },
    failed: { type: Boolean, default: false },
});
const emit = defineEmits<{ refresh: [] }>();
const lastGood = shallowRef<RedisMemorySection | null>(null);
watch(() => props.section, (section) => {
    if (section?.status === 'ready' && section.groups && section.total_bytes !== null && section.sampled_at) lastGood.value = section;
}, { immediate: true });
const series = computed(() => {
    const groups = lastGood.value?.groups;
    return groups ? redisMemoryGroups.map((key, index) => ({ key, name: t(`local.${key}`), value: groups[key], color: memoryColors[index] })) : [];
});

const i18nMessages = {
    'zh-cn': { local: {
        title: 'Redis 内存分布',
        pb_rankings: 'PB 榜',
        other_rankings: '其他排行榜',
        latest_videos: '最新录像',
        other: '其他',
        estimated: 'Redis 已分配内存（估算）',
        explanation: '包括其他数据库和 Redis 自身开销，与进程驻留内存的统计口径不同。',
    } },
    en: { local: {
        title: 'Redis Memory Distribution',
        pb_rankings: 'PB rankings',
        other_rankings: 'Other rankings',
        latest_videos: 'Latest videos',
        other: 'Other',
        estimated: 'Allocated Redis memory (estimated)',
        explanation: 'Includes other databases and Redis overhead. This differs from resident process memory.',
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
