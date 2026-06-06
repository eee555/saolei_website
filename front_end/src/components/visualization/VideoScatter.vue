<template>
    <div class="video-scatter">
        <div>
            <MSStatSelect v-model="x" label="x" :options="statOptions" class="stat-select" />
            <MSStatSelect v-model="y" label="y" :options="statOptions" class="stat-select" />
        </div>

        <div class="plot-legend">
            <span v-for="series in dataset" :key="series.level" class="plot-legend__item">
                <span
                    class="plot-legend__swatch"
                    :style="{ backgroundColor: series.color }"
                />
                {{ series.name }}
            </span>
        </div>

        <tippy :duration="0" sticky follow-cursor>
            <div ref="plotRef" class="plot-stage" @mouseleave="activePoint = null">
                <Grid :domain="domain" :padding="padding" :size="plotSize" :tick-count="5" :stroke="gridColor" />
                <Scatter
                    v-for="series in dataset" :key="series.level"
                    :domain="domain" :padding="padding" :size="plotSize"
                    :fill="series.color" :radius="VideoScatterConfig.radius"
                    :points="series.values"
                    @point-click="previewPoint"
                    @point-enter="setActivePoint"
                    @point-leave="clearActivePoint"
                />
                <Axes
                    :domain="domain" :padding="padding" :size="plotSize"
                    :label-color="labelColor" :stroke="axisColor" :tick-count="5"
                    :x-label="t(`common.prop.${x}`)"
                    :y-label="t(`common.prop.${y}`)"
                />
            </div>

            <template #content>
                <el-card v-if="activePoint" class="card-small">
                    <VideoAbstractDisplay :video="activePoint.video" />
                </el-card>
            </template>
        </tippy>
    </div>
</template>

<script setup lang="ts">
import '@/styles/cards.css';

import { ElCard } from 'element-plus';
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { Tippy } from 'vue-tippy';

import MSStatSelect from '@/components/Filters/MSStatSelect.vue';
import Axes from '@/components/visualization/Plots/Axes.vue';
import Grid from '@/components/visualization/Plots/Grid.vue';
import Scatter from '@/components/visualization/Plots/Scatter.vue';
import {
    defaultPlotPadding,
    getDataDomain,
    PlotPadding,
    PlotPoint,
} from '@/components/visualization/Plots/utils';
import VideoAbstractDisplay from '@/components/widgets/VideoAbstractDisplay.vue';
import { colorTheme, VideoScatterConfig } from '@/store';
import { getTextColor } from '@/utils/colors';
import { preview } from '@/utils/common/PlayerDialog';
import type { MS_Level } from '@/utils/ms_const';
import type { getStat_stat, VideoAbstract } from '@/utils/videoabstract';

const statOptions = ['time', 'bv', 'bvs', 'cl', 'ce', 'stnb'];
const levelOrder: MS_Level[] = ['b', 'i', 'e'];
const padding: PlotPadding = {
    ...defaultPlotPadding,
    left: 52,
    bottom: 42,
};

interface DataPoint extends PlotPoint {
    video: VideoAbstract;
}

const props = defineProps({
    videos: { type: Array<VideoAbstract>, default: () => [] },
});

const { t } = useI18n();
const x = ref<getStat_stat>('bv');
const y = ref<getStat_stat>('time');
const plotRef = ref<HTMLElement>();
const plotSize = ref({
    width: 640,
    height: 360,
});
const activePoint = ref<DataPoint | null>(null);
let resizeObserver: ResizeObserver | undefined;

function videoToDataPoint(video: VideoAbstract, statX: getStat_stat, statY: getStat_stat): DataPoint | undefined {
    const point = {
        x: video.getStat(statX),
        y: video.getStat(statY),
        video,
    };

    if (!Number.isFinite(point.x) || !Number.isFinite(point.y)) return undefined;
    return point as DataPoint;
}

function getDataset(level: MS_Level) {
    const values: DataPoint[] = [];

    props.videos.forEach((video) => {
        if (video.level !== level) return;
        const dataPoint = videoToDataPoint(video, x.value, y.value);
        if (dataPoint === undefined) return;
        values.push(dataPoint);
    });

    return values;
}

const dataset = computed(() => {
    return levelOrder.map((level) => ({
        level,
        name: t(`common.level.${level}`),
        color: colorTheme.value.level[level],
        values: getDataset(level),
    }));
});

const allPoints = computed(() => dataset.value.flatMap((series) => series.values));
const domain = computed(() => getDataDomain(allPoints.value));
const gridColor = computed(() => getComputedStyle(document.documentElement).getPropertyValue('--el-border-color-lighter'));
const axisColor = computed(() => getTextColor('regular'));
const labelColor = computed(() => getTextColor('regular'));

function updatePlotSize() {
    if (plotRef.value === undefined) return;

    const rect = plotRef.value.getBoundingClientRect();
    plotSize.value = {
        width: Math.max(1, rect.width),
        height: Math.max(1, rect.height),
    };
}

function setActivePoint(point: PlotPoint) {
    activePoint.value = point as DataPoint;
}

function clearActivePoint() {
    activePoint.value = null;
}

function previewPoint(point: PlotPoint) {
    preview((point as DataPoint).video.id);
}

onMounted(() => {
    updatePlotSize();
    resizeObserver = new ResizeObserver(updatePlotSize);
    if (plotRef.value !== undefined) resizeObserver.observe(plotRef.value);
});

onUnmounted(() => {
    resizeObserver?.disconnect();
});
</script>

<style lang="less" scoped>
.video-scatter {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.stat-select {
    min-width: 5em;
    width: 50%;
}

.plot-legend {
    align-items: center;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    padding: 8px 0;
}

.plot-legend__item {
    align-items: center;
    display: inline-flex;
    font-size: 12px;
    gap: 5px;
}

.plot-legend__swatch {
    border-radius: 50%;
    display: inline-block;
    height: 8px;
    width: 8px;
}

.plot-stage {
    flex-grow: 1;
    min-height: 300px;
    position: relative;
}

</style>
