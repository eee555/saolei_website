<template>
    <Tippy :duration="0" sticky follow-cursor>
        <div ref="plotRef" class="plot-stage">
            <Grid
                :domain="domain" :padding="padding" :size="plotSize"
                :stroke="gridColor" :x-ticks="xTicks" :y-ticks="yTicks"
            />
            <Scatter
                :domain="domain" :padding="padding" :size="plotSize"
                :fill-color="VideoScatterStore.scatterData.colors" :radius="VideoScatterConfig.radius"
                :points="VideoScatterStore.scatterData.points"
                @point-click="handlePointClick"
                @point-enter="handlePointEnter"
                @point-leave="activePoint = null;"
            />
            <Axes
                :domain="domain" :padding="padding" :size="plotSize"
                :label-color="labelColor" :stroke="axisColor"
                :x-ticks="xTicks" :y-ticks="yTicks"
                :x-label="t(`common.prop.${VideoScatterConfig.x}`)"
                :y-label="t(`common.prop.${VideoScatterConfig.y}`)"
            />
            <MouseDraw
                :mode="VideoScatterStore.canvasMode == 'select' ? 'rect' : ''"
                :size="plotSize"
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
import { computed, onMounted, onUnmounted, ref } from 'vue';
import type { PropType } from 'vue';
import { useI18n } from 'vue-i18n';
import { Tippy } from 'vue-tippy';

import { VideoScatterStore } from './store';

import { Axes, createLinearScale, Ellipse, getDataDomain, getNiceTicks, getPlotArea, Grid, MouseDraw, Rect, Scatter } from '@/components/visualization/Plots';
import type { AnyShape } from '@/components/visualization/Plots';
import type { PlotPadding, PlotPoint, PlotSize } from '@/components/visualization/Plots/utils';
import VideoAbstractDisplay from '@/components/widgets/VideoAbstractDisplay.vue';
import { VideoScatterConfig } from '@/store';
import { getTextColor } from '@/utils/colors';
import { preview } from '@/utils/common/PlayerDialog';
import type { VideoAbstract } from '@/utils/videoabstract';

const props = defineProps({
    padding: { type: Object as PropType<PlotPadding>, default: () => ({ top: 12, right: 16, bottom: 42, left: 52 }) },
});

const plotRef = ref<HTMLElement>();
const plotSize = ref<PlotSize>({
    width: 640,
    height: 360,
});
const activePoint = ref<PlotPoint<VideoAbstract> | null>(null);
let resizeObserver: ResizeObserver | undefined;

const domain = computed(() => getDataDomain(VideoScatterStore.scatterData.points));
const xTicks = computed(() => getNiceTicks(domain.value.xMin, domain.value.xMax, 5));
const yTicks = computed(() => getNiceTicks(domain.value.yMin, domain.value.yMax, 5));

const axisColor = computed(() => getTextColor('regular'));
const labelColor = computed(() => getTextColor('regular'));
const gridColor = computed(() => getComputedStyle(document.documentElement).getPropertyValue('--el-border-color-lighter'));

function handlePointClick(point: PlotPoint<VideoAbstract>) {
    preview(point.data.id);
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
    const area = getPlotArea(plotSize.value, props.padding);
    return createLinearScale(area.x, area.x + area.width, domain.value.xMin, domain.value.xMax);
}

function createSvgToDataYScale() {
    const area = getPlotArea(plotSize.value, props.padding);
    return createLinearScale(area.y + area.height, area.y, domain.value.yMin, domain.value.yMax);
}

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

const { t } = useI18n();
</script>

<style lang="less" scoped>
.plot-stage {
    flex-grow: 1;
    height: 500px;
    overflow: hidden;
    position: relative;
}
</style>
