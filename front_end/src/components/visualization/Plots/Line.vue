<template>
    <svg
        class="plot-line"
        :height="size.height" :width="size.width"
        :viewBox="`0 0 ${size.width} ${size.height}`"
        preserveAspectRatio="none"
    >
        <path
            v-if="pathData" :d="pathData"
            :stroke="stroke" :stroke-linecap="lineCap" :stroke-linejoin="lineJoin" :stroke-width="strokeWidth"
            fill="none" vector-effect="non-scaling-stroke"
        />
    </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { PropType } from 'vue';

import { defaultPlotPadding, getPlotArea, pointsToSvg } from './utils';
import type { PlotDomain, PlotPadding, PlotPoint, PlotSize } from './utils';

const props = defineProps({
    // Data points to connect in order. Scaling is done from the provided domain, not from these points.
    points: { type: Array as PropType<PlotPoint[]>, required: true },
    // Data-space bounds used to map point values onto the plot area.
    domain: { type: Object as PropType<PlotDomain>, required: true },
    // Outer SVG size in pixels. Parent components usually provide this from ResizeObserver.
    size: { type: Object as PropType<PlotSize>, default: () => ({ width: 320, height: 200 }) },
    // Insets shared with other plot layers so the line aligns with axes and grid.
    padding: { type: Object as PropType<PlotPadding>, default: () => defaultPlotPadding },
    // Line color.
    stroke: { type: String, default: '#2563eb' },
    // Line width in pixels.
    strokeWidth: { type: Number, default: 2 },
    // SVG stroke-linecap value controlling the shape of line endpoints.
    lineCap: { type: String as PropType<'butt' | 'round' | 'square'>, default: 'round' },
    // SVG stroke-linejoin value controlling how connected segments meet.
    lineJoin: { type: String as PropType<'bevel' | 'miter' | 'inherit' | 'round'>, default: 'round' },
});

const pathData = computed(() => {
    const area = getPlotArea(props.size, props.padding);
    const points = pointsToSvg(props.points, props.domain, area);

    if (points.length === 0) return '';

    return points.map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`).join(' ');
});
</script>

<style lang="less" scoped>
.plot-line {
    display: block;
    height: 100%;
    inset: 0;
    overflow: visible;
    pointer-events: none;
    position: absolute;
    width: 100%;
}
</style>
