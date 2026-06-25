<template>
    <Tippy class="video-scatter-tippy" :duration="0" sticky follow-cursor>
        <div ref="plotRef" class="plot-stage">
            <Grid
                :domain="VideoScatterStore.plotDomain"
                :padding="VideoScatterStore.plotPadding" :size="VideoScatterStore.plotSize"
                :stroke="gridColor" :x-ticks="xTicks" :y-ticks="yTicks"
            />
            <HighlightSelected v-if="VideoScatterConfig.highlightSelected" />
            <Scatter
                :domain="VideoScatterStore.plotDomain"
                :padding="VideoScatterStore.plotPadding"
                :size="VideoScatterStore.plotSize"
                :points="VideoScatterStore.scatterData.points"
                :fill-color="VideoScatterStore.fillColor"
                :radius="VideoScatterConfig.radius"
                :stroke-color="VideoScatterStore.fillColor"
                :stroke-width="VideoScatterStore.strokeWidth"
                :stroke-opacity="0.5"
                @point-click="handlePointClick"
                @point-enter="handlePointEnter"
                @point-leave="activePoint = null;"
            />
            <Axes
                :domain="VideoScatterStore.plotDomain"
                :padding="VideoScatterStore.plotPadding"
                :size="VideoScatterStore.plotSize"
                :label-color="labelColor" :stroke="axisColor"
                :x-ticks="xTicks" :y-ticks="yTicks"
                :x-label="t(`common.prop.${VideoScatterConfig.x}`)"
                :y-label="t(`common.prop.${VideoScatterConfig.y}`)"
            />
            <MouseDraw
                :mode="VideoScatterStore.canvasMode == 'select' ? 'rect' : ''"
                :size="VideoScatterStore.plotSize"
                @draw="handleDraw"
            />
        </div>

        <template #content>
            <ElCard v-if="activePoint" class="card-small">
                <VideoAbstractDisplay :video="activePoint.data" />
            </ElCard>
        </template>
    </Tippy>
</template>

<script setup lang="ts">
import '@/styles/cards.css';

import { ElCard } from 'element-plus';
import { computed, onMounted, onUnmounted, ref, useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';
import { Tippy } from 'vue-tippy';

import HighlightSelected from './HighlightSelected.vue';
import { VideoScatterStore } from './store';

import { Axes, createLinearScale, Ellipse, getNiceTicks, getPlotArea, Grid, MouseDraw, Rect, Scatter } from '@/components/visualization/Plots';
import type { AnyShape } from '@/components/visualization/Plots';
import type { PlotPoint } from '@/components/visualization/Plots/utils';
import VideoAbstractDisplay from '@/components/widgets/VideoAbstractDisplay.vue';
import { VideoScatterConfig } from '@/store';
import { getTextColor } from '@/utils/colors';
import { preview } from '@/utils/common/PlayerDialog';
import type { VideoAbstract } from '@/utils/videoabstract';

const plotRef = useTemplateRef<HTMLDivElement>('plotRef');
const activePoint = ref<PlotPoint<VideoAbstract> | null>(null);
let resizeObserver: ResizeObserver | undefined = undefined;

const xTicks = computed(() => getNiceTicks(VideoScatterStore.plotDomain.xMin, VideoScatterStore.plotDomain.xMax, 5));
const yTicks = computed(() => getNiceTicks(VideoScatterStore.plotDomain.yMin, VideoScatterStore.plotDomain.yMax, 5));

const axisColor = computed(() => getTextColor('regular'));
const labelColor = computed(() => getTextColor('regular'));
const gridColor = computed(() => getComputedStyle(document.documentElement).getPropertyValue('--el-border-color-lighter'));

function handlePointClick(point: PlotPoint<VideoAbstract>) {
    void preview(point.data.id);
}

function handlePointEnter(point: PlotPoint<VideoAbstract>) {
    activePoint.value = point;
}

function handleDraw(shape: AnyShape) {
    VideoScatterStore.selectionDraw(shapeToData(shape));
}

function shapeToData(shape: AnyShape): AnyShape {
    if (shape.type === 'ellipse') return ellipseToData(shape);
    return rectToData(shape);
}

function rectToData(shape: Rect): Rect {
    const scaleX = createSvgToDataXScale();
    const scaleY = createSvgToDataYScale();
    const x1 = scaleX(shape.x);
    const x2 = scaleX(shape.x + shape.width);
    const y1 = scaleY(shape.y);
    const y2 = scaleY(shape.y + shape.height);

    return new Rect(
        Math.min(x1, x2),
        Math.min(y1, y2),
        Math.abs(x2 - x1),
        Math.abs(y2 - y1),
    );
}

function ellipseToData(shape: Ellipse): Ellipse {
    const scaleX = createSvgToDataXScale();
    const scaleY = createSvgToDataYScale();
    const cx = scaleX(shape.cx);
    const cy = scaleY(shape.cy);

    return new Ellipse(
        cx,
        cy,
        Math.abs(scaleX(shape.cx + shape.rx) - cx),
        Math.abs(scaleY(shape.cy + shape.ry) - cy),
    );
}

function createSvgToDataXScale() {
    const area = getPlotArea(VideoScatterStore.plotSize, VideoScatterStore.plotPadding);
    return createLinearScale(area.x, area.x + area.width, VideoScatterStore.plotDomain.xMin, VideoScatterStore.plotDomain.xMax);
}

function createSvgToDataYScale() {
    const area = getPlotArea(VideoScatterStore.plotSize, VideoScatterStore.plotPadding);
    return createLinearScale(area.y + area.height, area.y, VideoScatterStore.plotDomain.yMin, VideoScatterStore.plotDomain.yMax);
}

function updatePlotSize() {
    if (plotRef.value === null) return;

    const rect = plotRef.value.getBoundingClientRect();
    VideoScatterStore.plotSize = {
        width: Math.max(1, rect.width),
        height: Math.max(1, rect.height),
    };
}

onMounted(() => {
    updatePlotSize();
    resizeObserver = new ResizeObserver(updatePlotSize);
    if (plotRef.value !== null) resizeObserver.observe(plotRef.value);
});

onUnmounted(() => {
    resizeObserver?.disconnect();
});

const { t } = useI18n();
</script>

<style lang="less" scoped>
.video-scatter-tippy {
    flex: 1 1 auto;
    min-height: 0;
}

.plot-stage {
    height: 100%;
    overflow: hidden;
    position: relative;
    width: 100%;
}
</style>
