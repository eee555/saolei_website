<template>
    <RefreshableCard data-statistic="tasks" class="statistics-card" :title="t('local.title')" :loading="loading" @refresh="refresh">
        <p v-if="failed" role="alert" class="text-danger">
            {{ t('statistics.requestFailed') }}
            <span v-if="total !== null">{{ t('statistics.previous') }}</span>
        </p>
        <p v-if="loading && total === null" role="status">
            {{ t('statistics.loading') }}
        </p>
        <template v-if="total !== null">
            <VueUiDonut v-if="total > 0" :dataset="dataset" :config="config" />
            <p v-else role="status">
                {{ t('statistics.empty') }}
            </p>
            <div class="statistics-total">
                {{ t('statistics.total') }}: {{ formatCount(total) }}
            </div>
        </template>
        <p v-else-if="!loading && !failed" role="status">
            {{ t('statistics.unavailable') }}
        </p>
        <p class="statistics-cache-note">
            {{ t('local.cache') }}
        </p>
    </RefreshableCard>
</template>

<script setup lang="ts">
import 'vue-data-ui/style.css';
import './statistics.css';
import { computed } from 'vue';
import type { VueUiDonutConfig } from 'vue-data-ui';
import { VueUiDonut } from 'vue-data-ui';
import { useI18n } from 'vue-i18n';

import { statisticsColors } from './statistics';
import { useStatistic } from './useStatistic';

import RefreshableCard from '@/components/common/RefreshableCard.vue';
import { local } from '@/store';

const statuses = ['READY', 'RUNNING', 'SUCCESSFUL', 'FAILED'] as const;
interface TaskSummary {
    total: number;
    status: Record<typeof statuses[number], number>;
}

const { data, loading, failed, refresh } = useStatistic<TaskSummary>('/api/monitor/tasksummary');
const total = computed(() => data.value?.total ?? null);
const dataset = computed(() => (data.value === null
    ? []
    : statuses.map((key, index) => ({
        key, name: t(`local.${key}`), values: [data.value?.status[key] ?? 0], color: statisticsColors[index],
    }))));

function formatCount(value: number) {
    return new Intl.NumberFormat(locale.value).format(value);
}

const config = computed<VueUiDonutConfig>(() => ({
    theme: local.value.darkmode ? 'dark' : '',
    useCssAnimation: false,
    userOptions: { show: false },
    style: { chart: {
        backgroundColor: 'transparent',
        legend: { show: true, showValue: true, showPercentage: true, roundingPercentage: 1, fontSize: 12, backgroundColor: 'transparent' },
        tooltip: { show: false },
        layout: { labels: {
            value: { formatter: ({ value }) => formatCount(value) },
            hollow: {
                average: { show: false },
                total: { text: t('statistics.total'), value: { formatter: ({ value }) => formatCount(value) } },
            },
        } },
    } },
}));

const i18nMessages = {
    'zh-cn': { local: {
        cache: '数据缓存 5 分钟，刷新不会跳过缓存。',
        title: '后台任务',
        READY: '排队中',
        RUNNING: '运行中',
        SUCCESSFUL: '已完成',
        FAILED: '失败',
    } },
    en: { local: {
        cache: 'Cached for 5 minutes. Refresh uses the same cache.',
        title: 'Background tasks',
        READY: 'Ready',
        RUNNING: 'Running',
        SUCCESSFUL: 'Successful',
        FAILED: 'Failed',
    } },
};
const { t, locale } = useI18n({ messages: i18nMessages });
</script>
