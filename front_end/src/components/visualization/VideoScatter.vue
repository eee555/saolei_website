<template>
    <div class="video-scatter">
        <div style="display: flex; flex-wrap: wrap; gap: 2em">
            <div style="width: 14em; display: flex; gap: 1em">
                <MSStatSelect v-model="x" label="x" :options="statOptions" />
                <MSStatSelect v-model="y" label="y" :options="statOptions" />
            </div>
            <div style="display: flex; gap: 1em; text-align: center">
                <span v-for="level in ['b', 'i', 'e']">
                    <ElColorPicker v-model="colorTheme.level[level]" size="small" />
                    <span class="text">
                        {{ t(`common.level.${level}`) }}
                    </span>
                </span>
            </div>
            <div>
                <MarkerSetting
                    v-model:radius="VideoScatterConfig.radius"
                    options="radius"
                />
            </div>
        </div>

        <Tippy :duration="0" sticky follow-cursor>
            <div ref="plotRef" class="plot-stage">
                <Grid
                    :domain="domain" :padding="padding" :size="plotSize"
                    :stroke="gridColor" :x-ticks="xTicks" :y-ticks="yTicks"
                />
                <Scatter
                    v-for="series in dataset" :key="series.level"
                    :domain="domain" :padding="padding" :size="plotSize"
                    :fill="series.color" :radius="VideoScatterConfig.radius"
                    :points="series.values"
                    @point-click="handlePointClick"
                    @point-enter="handlePointEnter"
                    @point-leave="activePoint = null;"
                />
                <Axes
                    :domain="domain" :padding="padding" :size="plotSize"
                    :label-color="labelColor" :stroke="axisColor"
                    :x-ticks="xTicks" :y-ticks="yTicks"
                    :x-label="t(`common.prop.${x}`)"
                    :y-label="t(`common.prop.${y}`)"
                />
            </div>

            <template #content>
                <el-card v-if="activePoint" class="card-small">
                    <VideoAbstractDisplay :video="activePoint.data" />
                </el-card>
            </template>
        </Tippy>
    </div>
</template>

<script setup lang="ts">
import '@/styles/cards.css';
import '@/styles/text.css';

import { ElCard, ElColorPicker } from 'element-plus';
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { Tippy } from 'vue-tippy';

import MSStatSelect from '@/components/Filters/MSStatSelect.vue';
import { Axes, Grid, MarkerSetting, Scatter } from '@/components/visualization/Plots';
import { defaultPlotPadding, getDataDomain, getNiceTicks, PlotPadding, PlotPoint } from '@/components/visualization/Plots/utils';
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
const activePoint = ref<PlotPoint<VideoAbstract> | null>(null);
let resizeObserver: ResizeObserver | undefined;

function videoToDataPoint(video: VideoAbstract, statX: getStat_stat, statY: getStat_stat): PlotPoint<VideoAbstract> | undefined {
    const point = {
        x: video.getStat(statX),
        y: video.getStat(statY),
        data: video,
    };

    if (!Number.isFinite(point.x) || !Number.isFinite(point.y)) return undefined;
    return point as PlotPoint<VideoAbstract>;
}

function getDataset(level: MS_Level) {
    const values: PlotPoint<VideoAbstract>[] = [];

    props.videos.forEach((video) => {
        if (video.level !== level) return;
        const dataPoint = videoToDataPoint(video, x.value, y.value);
        if (dataPoint === undefined) return;
        values.push(dataPoint);
    });

    return values;
}

function handlePointClick(point: PlotPoint<VideoAbstract>) {
    preview(point.data.id);
}

function handlePointEnter(point: PlotPoint<VideoAbstract>) {
    activePoint.value = point;
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
const xTicks = computed(() => getNiceTicks(domain.value.xMin, domain.value.xMax, 5));
const yTicks = computed(() => getNiceTicks(domain.value.yMin, domain.value.yMax, 5));
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
    flex-grow: 1;
    gap: 1em;
}

.plot-stage {
    flex-grow: 1;
    overflow: hidden;
    height: 500px;
    position: relative;
}

.config-panel {
    display: flex;
    flex-wrap: wrap;
    gap: 2em;
    align-items: center;
}
</style>
