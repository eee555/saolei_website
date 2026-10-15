<template>
    <RefreshableCard data-statistic="videos" class="statistics-card" :title="t('local.title')" :loading="loading" @refresh="refresh">
        <div class="video-dimensions" role="group" :aria-label="t('local.dimension')">
            <BaseTextButton v-for="key in dimensions" :key="key" size="small" :aria-pressed="dimension === key" @click="dimension = key">
                {{ t(`common.prop.${key}`) }}
            </BaseTextButton>
        </div>
        <p v-if="failed" role="alert" class="text-danger">
            {{ t('statistics.requestFailed') }}
            <span v-if="total !== null">{{ t('statistics.previous') }}</span>
        </p>
        <p v-if="loading && total === null" role="status">
            {{ t('statistics.loading') }}
        </p>
        <template v-if="total !== null">
            <div class="video-panels">
                <div v-for="panel in panels" :key="panel.key" class="video-panel" :data-dimension="panel.key" :aria-hidden="panel.key !== dimension" :inert="panel.key !== dimension">
                    <VueUiDonut v-if="panel.total > 0" :dataset="panel.dataset" :config="config" />
                    <p v-else role="status">
                        {{ t('statistics.empty') }}
                    </p>
                </div>
            </div>
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
import { computed, ref } from 'vue';
import type { VueUiDonutConfig } from 'vue-data-ui';
import { VueUiDonut } from 'vue-data-ui';
import { useI18n } from 'vue-i18n';

import { statisticsColors } from './statistics';
import { useStatistic } from './useStatistic';

import BaseTextButton from '@/components/common/BaseTextButton.vue';
import RefreshableCard from '@/components/common/RefreshableCard.vue';
import { local } from '@/store';
import { MS_Levels, MS_Mode, MS_Softwares, MS_State } from '@/utils/ms_const';

const dimensions = ['software', 'level', 'mode', 'state'] as const;
type Dimension = typeof dimensions[number];
type VideoSummary = { total: number } & Record<Dimension, Record<string, number>>;
const dimension = ref<Dimension>('software');
const orders: Record<Dimension, readonly string[]> = {
    software: MS_Softwares, level: MS_Levels, mode: Object.values(MS_Mode), state: Object.values(MS_State),
};
const extraModes = ['07', '08', '09'];
const omittedCategories: Record<Dimension, readonly string[]> = {
    software: [], level: [], mode: ['01', '04', MS_Mode.Recursive], state: ['e'],
};
const { data, loading, failed, refresh } = useStatistic<VideoSummary>('/api/monitor/videosummary');
const panels = computed(() => dimensions.map((panelDimension) => {
    const counts: Record<string, number> = data.value?.[panelDimension] ?? {};
    const order = orders[panelDimension];
    const keys = [...order, ...Object.keys(counts).filter((key) => !order.includes(key)).sort()].filter((key) => !omittedCategories[panelDimension].includes(key));
    const dataset = keys.map((key, index) => ({
        key, name: categoryName(key, panelDimension), values: [counts[key] ?? 0], color: statisticsColors[index % statisticsColors.length],
    }));
    return { key: panelDimension, dataset, total: dataset.reduce((sum, item) => sum + item.values[0], 0) };
}));
const currentPanel = computed(() => panels.value.find((panel) => panel.key === dimension.value));
const total = computed(() => (data.value === null ? null : currentPanel.value?.total ?? 0));

function categoryName(key: string, panelDimension: Dimension) {
    if (panelDimension === 'mode') {
        if (extraModes.includes(key)) return t(`local.mode${key}`);
        return orders.mode.includes(key) ? t(`common.mode.code${key}`) : key;
    }
    if (panelDimension === 'level') {
        const custom = (/^c(\d+)_(\d+)_(\d+)$/).exec(key);
        if (custom) return t('common.level.c', { row: custom[1], column: custom[2], mine: custom[3] });
    }
    return orders[panelDimension].includes(key) ? t(`common.${panelDimension}.${key}`) : key;
}

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
        title: '录像统计',
        dimension: '统计维度',
        mode07: '弱无猜',
        mode08: '准无猜',
        mode09: '强可猜',
    } },
    en: { local: {
        cache: 'Cached for 5 minutes. Refresh uses the same cache.',
        title: 'Video Statistics',
        dimension: 'Statistics dimension',
        mode07: 'Weak No Guessing',
        mode08: 'Partial No Guessing',
        mode09: 'Strong Guessing',
    } },
};
const { t, locale } = useI18n({ messages: i18nMessages });
</script>

<style scoped>
.video-panels {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
}
.video-panel {
    grid-area: 1 / 1;
    align-self: start;
    min-width: 0;
}
.video-panel[aria-hidden="true"] {
    visibility: hidden;
}
.video-dimensions {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-top: 8px;
}
.video-dimensions button[aria-pressed="true"] {
    color: var(--ui-color-primary);
    background: var(--ui-fill-color-light);
    box-shadow: inset 0 -2px var(--ui-color-primary);
}
</style>
