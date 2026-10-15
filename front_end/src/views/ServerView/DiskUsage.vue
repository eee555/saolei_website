<template>
    <RefreshableCard data-statistic="disk" class="statistics-card" :title="t('local.title')" :loading="loading" @refresh="refresh">
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
                {{ t('statistics.total') }}: {{ formatBytes(total) }}
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
import { formatBytes } from '@/utils/strings';

interface DiskUsage {
    total: number;
    used: number;
    free: number;
    video: number | null;
    db: number | null;
}

const { data, loading, failed, refresh } = useStatistic<DiskUsage>('/api/monitor/diskusage', (disk) => {
    const values = [disk.total, disk.free, disk.video ?? 0, disk.db ?? 0];
    if (values.some((value) => !Number.isFinite(value) || value < 0) || disk.free + (disk.video ?? 0) + (disk.db ?? 0) > disk.total) {
        throw new RangeError('Disk categories exceed the reported volume');
    }
});
const total = computed(() => data.value?.total ?? null);
const dataset = computed(() => {
    if (data.value === null) return [];
    const { total: diskTotal, free, video, db } = data.value;
    return [
        { key: 'video', name: t('local.video'), values: [video ?? 0], color: statisticsColors[0] },
        { key: 'db', name: t('local.db'), values: [db ?? 0], color: statisticsColors[1] },
        { key: 'other', name: t('local.other'), values: [diskTotal - free - (video ?? 0) - (db ?? 0)], color: statisticsColors[5] },
        { key: 'free', name: t('local.free'), values: [free], color: statisticsColors[2] },
    ];
});

const config = computed<VueUiDonutConfig>(() => ({
    theme: local.value.darkmode ? 'dark' : '',
    useCssAnimation: false,
    userOptions: { show: false },
    style: { chart: {
        backgroundColor: 'transparent',
        legend: { show: true, showValue: true, showPercentage: true, roundingPercentage: 1, fontSize: 12, backgroundColor: 'transparent' },
        tooltip: { show: false },
        layout: { labels: {
            value: { formatter: ({ value }) => formatBytes(value) },
            hollow: {
                average: { show: false },
                total: { text: t('statistics.total'), value: { formatter: ({ value }) => formatBytes(value) } },
            },
        } },
    } },
}));

const i18nMessages = {
    'zh-cn': { local: {
        cache: '数据缓存 5 分钟，刷新不会跳过缓存。',
        title: '磁盘使用情况',
        video: '录像文件',
        db: '数据库',
        other: '其他文件',
        free: '可用空间',
    } },
    en: { local: {
        cache: 'Cached for 5 minutes. Refresh uses the same cache.',
        title: 'Disk Usage',
        video: 'Videos',
        db: 'Database',
        other: 'Other',
        free: 'Free',
    } },
};
const { t } = useI18n({ messages: i18nMessages });
</script>
