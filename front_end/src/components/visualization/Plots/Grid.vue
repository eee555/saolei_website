<template>
    <svg
        class="plot-grid"
        :height="size.height" :width="size.width"
        :viewBox="`0 0 ${size.width} ${size.height}`"
        preserveAspectRatio="none"
    >
        <line
            v-for="tick in xTicks" :key="`x-${tick}`"
            :stroke="stroke" :stroke-dasharray="dashArray" :stroke-width="strokeWidth"
            :x1="xScale(tick)" :x2="xScale(tick)"
            :y1="area.y" :y2="area.y + area.height"
            vector-effect="non-scaling-stroke"
        />
        <line
            v-for="tick in yTicks" :key="`y-${tick}`"
            :stroke="stroke" :stroke-dasharray="dashArray" :stroke-width="strokeWidth"
            :x1="area.x" :x2="area.x + area.width"
            :y1="yScale(tick)" :y2="yScale(tick)"
            vector-effect="non-scaling-stroke"
        />
    </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { PropType } from 'vue';

import { createLinearScale, defaultPlotPadding, getPlotArea } from './utils';
import type { PlotDomain, PlotPadding, PlotSize } from './utils';

const props = defineProps({
    // Data-space bounds used to place grid lines.
    domain: { type: Object as PropType<PlotDomain>, required: true },
    // Outer SVG size in pixels. Parent components usually provide this from ResizeObserver.
    size: { type: Object as PropType<PlotSize>, default: () => ({ width: 320, height: 200 }) },
    // Insets shared with other plot layers so grid lines align with axes and data.
    padding: { type: Object as PropType<PlotPadding>, default: () => defaultPlotPadding },
    // X-axis grid positions in data-space coordinates.
    xTicks: { type: Array as PropType<number[]>, default: () => [] },
    // Y-axis grid positions in data-space coordinates.
    yTicks: { type: Array as PropType<number[]>, default: () => [] },
    // Grid line color.
    stroke: { type: String, default: '#d4d4d8' },
    // Grid line width in pixels.
    strokeWidth: { type: Number, default: 1 },
    // SVG stroke-dasharray value, for example "4 4" for dashed grid lines.
    dashArray: { type: String, default: '' },
    // Reserved for API symmetry with axes; this component does not render labels.
    labelColor: { type: String, default: '#52525b' },
    // Reserved for API symmetry with axes; this component does not render text.
    fontSize: { type: Number, default: 11 },
    // Reserved for API symmetry with axes; this component does not render axis titles.
    xLabel: { type: String, default: '' },
    // Reserved for API symmetry with axes; this component does not render axis titles.
    yLabel: { type: String, default: '' },
});

const area = computed(() => getPlotArea(props.size, props.padding));
const xScale = computed(() => createLinearScale(props.domain.xMin, props.domain.xMax, area.value.x, area.value.x + area.value.width));
const yScale = computed(() => createLinearScale(props.domain.yMin, props.domain.yMax, area.value.y + area.value.height, area.value.y));
</script>

<style lang="less" scoped>
.plot-grid {
    display: block;
    height: 100%;
    inset: 0;
    overflow: visible;
    pointer-events: none;
    position: absolute;
    width: 100%;
}
</style>
