<template>
    <svg
        class="plot-scatter"
        :height="size.height" :width="size.width"
        :viewBox="`0 0 ${size.width} ${size.height}`"
        preserveAspectRatio="none"
    >
        <circle
            v-for="(point, index) in renderedPoints" :key="index" class="plot-scatter__point"
            :cx="point.x" :cy="point.y" :r="radius"
            :fill-opacity="getMaybeArray(opacity,point.index)"
            :fill="getMaybeArray(fillColor, point.index)"
            :stroke="getMaybeArray(strokeColor, point.index)"
            :stroke-width="getMaybeArray(strokeWidth, point.index)"
            vector-effect="non-scaling-stroke"
            @click="console.log('point-click'); emit('point-click', points[point.index])"
            @mouseenter="emit('point-enter', points[point.index])"
            @mouseleave="emit('point-leave', points[point.index])"
        />
    </svg>
</template>

<script setup lang="ts" generic="T = unknown">
import { computed } from 'vue';
import type { PropType } from 'vue';

import { defaultPlotPadding, getPlotArea, pointToSvg } from './utils';
import type { PlotDomain, PlotPadding, PlotPoint, PlotSize } from './utils';

const props = defineProps({
    // Data points to render. Scaling is done from the provided domain, not from these points.
    points: { type: Array as PropType<PlotPoint<T>[]>, required: true },
    // Data-space bounds used to map point values onto the plot area.
    domain: { type: Object as PropType<PlotDomain>, required: true },
    // Outer SVG size in pixels. Parent components usually provide this from ResizeObserver.
    size: { type: Object as PropType<PlotSize>, default: () => ({ width: 320, height: 200 }) },
    // Insets shared with other plot layers so points align with axes and grid.
    padding: { type: Object as PropType<PlotPadding>, default: () => defaultPlotPadding },
    // Circle radius in pixels.
    radius: { type: Number, default: 3 },
    // Circle fill color.
    fillColor: { type: [String, Array] as PropType<string | string[]>, default: '#2563eb' },
    // Point opacity. Pass a number for all points or an array aligned with the input points.
    opacity: { type: [Number, Array] as PropType<number | number[]>, default: 1 },
    // Circle outline color. Use "none" to hide the outline.
    strokeColor: { type: [String, Array] as PropType<string | string[]>, default: 'none' },
    // Circle outline width in pixels.
    strokeWidth: { type: [Number, Array] as PropType<number | number[]>, default: 0 },
});

const emit = defineEmits<{
    (e: 'point-click', point: PlotPoint<T>): void;
    (e: 'point-enter', point: PlotPoint<T>): void;
    (e: 'point-leave', point: PlotPoint<T>): void;
}>();

function getMaybeArray<T>(arr: T | T[], index: number) {
    return Array.isArray(arr) ? arr[index] : arr;
}

const renderedPoints = computed(() => {
    const area = getPlotArea(props.size, props.padding);

    return props.points.
        map((point, index) => ({ point, index })).
        filter(({ point }) => Number.isFinite(point.x) && Number.isFinite(point.y)).
        map(({ point, index }) => ({
            ...pointToSvg(point, props.domain, area),
            index: index,
        }));
});
</script>

<style lang="less" scoped>
.plot-scatter {
    display: block;
    height: 100%;
    inset: 0;
    overflow: visible;
    pointer-events: none;
    position: absolute;
    width: 100%;
}

.plot-scatter__point {
    cursor: pointer;
    pointer-events: auto;
}
</style>
