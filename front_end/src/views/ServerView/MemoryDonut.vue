<template>
    <BaseCardNormal class="memory-card" :aria-busy="loading">
        <header class="memory-header">
            <h2>{{ title }}</h2>
            <BaseTextButton size="small" :disabled="loading" @click="emit('refresh')">
                {{ t('local.refresh') }}
            </BaseTextButton>
        </header>
        <p v-if="failed || reason" role="alert" class="memory-error">
            {{ failed ? t('local.request_failed') : t(`local.${reason}`) }}
            <span v-if="total !== null">{{ t('local.previous') }}</span>
        </p>
        <p v-if="loading && total === null" role="status">
            {{ t('local.loading') }}
        </p>
        <template v-if="total !== null">
            <VueUiDonut v-if="total > 0" :dataset="dataset" :config="config" />
            <p v-else role="status">
                {{ t('local.empty') }}
            </p>
            <dl class="memory-legend">
                <div v-for="item in series" :key="item.key" :data-group="item.key">
                    <dt><i :style="{ backgroundColor: item.color }" aria-hidden="true" />{{ item.name }}</dt>
                    <dd>{{ formatBytes(item.value) }} · {{ total ? (item.value / total * 100).toFixed(1) : '0.0' }}%</dd>
                </div>
            </dl>
            <div class="memory-total">
                {{ t('local.total') }}: {{ formatBytes(total) }}
            </div>
            <slot />
            <div v-if="sampledAt" class="memory-time">
                {{ t('local.sampled') }}: <time :datetime="sampledAt">{{ new Date(sampledAt).toLocaleString(locale) }}</time>
            </div>
        </template>
        <p v-else-if="!loading && !failed && !reason" role="status">
            {{ t('local.unavailable') }}
        </p>
        <p class="memory-cache-note">
            {{ t('local.cache') }}
        </p>
    </BaseCardNormal>
</template>

<script setup lang="ts">
import 'vue-data-ui/style.css';
import type { PropType } from 'vue';
import { computed } from 'vue';
import type { VueUiDonutConfig } from 'vue-data-ui';
import { VueUiDonut } from 'vue-data-ui';
import { useI18n } from 'vue-i18n';

import type { MemoryFailureReason, MemorySeries } from './memory';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import BaseTextButton from '@/components/common/BaseTextButton.vue';
import { local } from '@/store';
import { formatBytes } from '@/utils/strings';

const props = defineProps({
    title: { type: String, required: true },
    series: { type: Array as PropType<MemorySeries[]>, required: true },
    total: { type: Number as PropType<number | null>, default: null },
    sampledAt: { type: String as PropType<string | null>, default: null },
    loading: { type: Boolean, default: false },
    failed: { type: Boolean, default: false },
    reason: { type: String as PropType<MemoryFailureReason | null>, default: null },
});
const emit = defineEmits<{ refresh: [] }>();
defineSlots<{ default?: () => unknown }>();

const dataset = computed(() => props.series.map((item) => ({ name: item.name, color: item.color, values: [item.value] })));
const config = computed<VueUiDonutConfig>(() => ({
    theme: local.value.darkmode ? 'dark' : '',
    useCssAnimation: false,
    userOptions: { show: false },
    style: { chart: {
        backgroundColor: 'transparent',
        legend: { show: false },
        tooltip: { show: false },
        layout: { labels: {
            value: { formatter: ({ value }) => formatBytes(value) },
            hollow: {
                average: { show: false },
                total: { text: t('local.total'), value: { formatter: ({ value }) => formatBytes(value) } },
            },
        } },
    } },
}));

const i18nMessages = {
    'zh-cn': { local: {
        refresh: '刷新',
        loading: '正在获取内存数据…',
        empty: '当前内存占用为 0。',
        unavailable: '暂无内存数据。',
        request_failed: '内存数据请求失败，请重试。',
        previous: '正在显示上次成功获取的数据。',
        total: '合计',
        sampled: '采集时间',
        cache: '数据缓存 5 分钟，刷新不会跳过缓存。',
        permission_denied: '没有权限读取完整的进程内存。',
        unsupported_metric: '当前系统不支持所需的内存统计。',
        unsupported_scope: '当前部署无法完整统计本机服务内存。',
        budget_exceeded: '内存采集超出本次处理预算。',
        metadata_unavailable: 'PB 榜的缓存索引暂不可用。',
        inconsistent_snapshot: '本次内存数据不一致，请稍后重试。',
        redis_unavailable: '暂时无法读取 Redis 内存。',
        database_unavailable: '暂时无法取得 PB 用户索引。',
        collection_failed: '本次内存采集失败。',
    } },
    en: { local: {
        refresh: 'Refresh',
        loading: 'Loading memory data…',
        empty: 'Current memory usage is zero.',
        unavailable: 'Memory data is not available.',
        request_failed: 'Could not load memory data. Please retry.',
        previous: 'Showing the last successful result.',
        total: 'Total',
        sampled: 'Sampled at',
        cache: 'Cached for 5 minutes. Refresh uses the same cache.',
        permission_denied: 'Permission to read complete process memory is missing.',
        unsupported_metric: 'The required memory metric is not supported.',
        unsupported_scope: 'This deployment cannot report all local service memory.',
        budget_exceeded: 'Memory collection exceeded its processing budget.',
        metadata_unavailable: 'The PB cache index is not available.',
        inconsistent_snapshot: 'This memory sample is inconsistent. Please retry later.',
        redis_unavailable: 'Redis memory is temporarily unavailable.',
        database_unavailable: 'The PB user index is temporarily unavailable.',
        collection_failed: 'Memory collection failed.',
    } },
};
const { t, locale } = useI18n({ messages: i18nMessages });
</script>

<style scoped>
.memory-card {
    min-width: 0;
}
.memory-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
}
.memory-header h2 {
    margin: 0;
    font-size: var(--ui-font-size-medium);
}
.memory-legend {
    margin: 6px 0;
}
.memory-legend > div {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 2px 8px;
    padding: 2px 0;
}
.memory-legend dt {
    display: flex;
    align-items: center;
    gap: 5px;
}
.memory-legend i {
    width: 9px;
    height: 9px;
    flex-shrink: 0;
}
.memory-legend dd {
    margin: 0 0 0 auto;
    font-variant-numeric: tabular-nums;
}
.memory-total {
    font-weight: 600;
}
.memory-error {
    color: var(--ui-color-danger);
}
.memory-time, .memory-cache-note {
    font-size: var(--ui-font-size-small);
    color: var(--ui-text-color-secondary);
    overflow-wrap: anywhere;
}
.memory-cache-note {
    margin: 6px 0 0;
}
</style>
