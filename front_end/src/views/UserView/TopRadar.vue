<template>
    <figure class="top-radar" :data-nf="nf" :aria-label="title">
        <VueUiRadar :dataset="dataset" :config="config">
            <template v-if="nf" #svg="{ svg }">
                <text class="top-radar-mark" :x="svg.width / 2" :y="svg.height / 2" text-anchor="middle" dominant-baseline="middle" aria-hidden="true">
                    NF
                </text>
            </template>
            <template #tooltip="{ seriesIndex }">
                <div class="top-radar-tooltip">
                    <strong>{{ rows[seriesIndex]?.name }}</strong>
                    <div v-for="row in tooltipRows(seriesIndex)" :key="row.name">
                        {{ row.name }}: {{ row.value }}
                    </div>
                </div>
            </template>
        </VueUiRadar>
    </figure>
</template>

<script setup lang="ts">
import 'vue-data-ui/style.css';
import { computed } from 'vue';
import type { PropType } from 'vue';
import { VueUiRadar } from 'vue-data-ui';
import type { VueUiRadarConfig, VueUiRadarDataset } from 'vue-data-ui';
import { useI18n } from 'vue-i18n';

import { formatTopValue, missingTopValue, topAxes, topField, topRadius, topStatNames } from '@/services/topRankingService';
import type { TopAnchors, TopRecords } from '@/services/topRankingService';
import { local } from '@/store';

const props = defineProps({
    records: { type: Object as PropType<TopRecords>, required: true },
    anchors: { type: Object as PropType<TopAnchors>, required: true },
    nf: { type: Boolean, default: false },
});
const title = computed(() => (props.nf ? 'NF top' : 'top'));
const anchorLabel = computed(() => t(props.nf ? 'local.nfAnchor' : 'local.ordinaryAnchor'));
const rows = computed(() => topAxes.map(({ level, stat }) => {
    const field = topField(props.nf, level, stat);
    const anchor = props.anchors[field]?.value ?? 0;
    const value = props.records[field]?.mean ?? missingTopValue(stat);
    return { level, stat, name: `${t(`common.level.${level}`)} ${t(`common.prop.${topStatNames[stat]}`)}`, value, anchor, radius: topRadius(value, anchor, stat) };
}));
const dataset = computed<VueUiRadarDataset>(() => ({
    categories: [{ name: t('local.personal'), color: '#67C23A' }],
    series: rows.value.map((row) => ({ name: row.name, values: [row.radius], target: row.anchor > 0 ? 100 : 0 })),
}));

function tooltipRows(index: number) {
    if (index < 0 || index >= rows.value.length) return [];
    const row = rows.value[index];
    return [
        { name: t('local.personal'), value: formatTopValue(row.value, row.level, row.stat) },
        { name: anchorLabel.value, value: formatTopValue(row.anchor, row.level, row.stat) },
    ];
}

const config = computed<VueUiRadarConfig>(() => ({
    theme: local.value.darkmode ? 'dark' : '',
    useCssAnimation: false,
    userOptions: { show: false },
    style: { chart: {
        backgroundColor: 'transparent',
        layout: {
            dataPolygon: { useGradient: false, opacity: 12, strokeWidth: 2 },
            targetReference: { show: true, stroke: props.nf ? '#E6A23C' : '#409EFF', strokeWidth: 2, strokeDasharray: 4, showInLegend: true, legendLabel: anchorLabel.value },
            labels: { dataLabels: { fontSize: 11 } },
        },
        legend: { show: false },
        tooltip: { show: true, showPercentage: false, roundingValue: 1 },
    } },
}));

const i18nMessages = {
    'zh-cn': { local: {
        personal: '玩家',
        ordinaryAnchor: 'Top 锚点',
        nfAnchor: 'NF Top 锚点',
    } },
    en: { local: {
        personal: 'Player',
        ordinaryAnchor: 'Top anchor',
        nfAnchor: 'NF Top anchor',
    } },
};
const { t } = useI18n({ messages: i18nMessages });
</script>

<style scoped>
.top-radar {
    min-width: 0;
    width: 100%;
    margin: 0;
}
.top-radar-mark {
    fill: var(--el-text-color-primary);
    font-size: 72px;
    font-weight: 700;
    opacity: 0.16;
    pointer-events: none;
}
.top-radar-tooltip {
    text-align: start;
    font-size: var(--ui-font-size-small);
}
</style>
