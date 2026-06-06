<template>
    <svg
        class="plot-grid"
        :height="size.height" :width="size.width"
        :viewBox="`0 0 ${size.width} ${size.height}`"
        preserveAspectRatio="none"
    >
        <line
            v-for="tick in resolvedXTicks" :key="`x-${tick}`"
            :stroke="stroke" :stroke-dasharray="dashArray" :stroke-width="strokeWidth"
            :x1="xScale(tick)" :x2="xScale(tick)"
            :y1="area.y" :y2="area.y + area.height"
            vector-effect="non-scaling-stroke"
        />
        <line
            v-for="tick in resolvedYTicks" :key="`y-${tick}`"
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

import { createLinearScale, defaultPlotPadding, getNiceTicks, getPlotArea } from './utils';
import type { PlotDomain, PlotPadding, PlotSize } from './utils';

const props = defineProps({
    domain: { type: Object as PropType<PlotDomain>, required: true },
    size: { type: Object as PropType<PlotSize>, default: () => ({ width: 320, height: 200 }) },
    padding: { type: Object as PropType<PlotPadding>, default: () => defaultPlotPadding },
    xTicks: { type: Array as PropType<number[]>, default: undefined },
    yTicks: { type: Array as PropType<number[]>, default: undefined },
    tickCount: { type: Number, default: 5 },
    stroke: { type: String, default: '#d4d4d8' },
    strokeWidth: { type: Number, default: 1 },
    dashArray: { type: String, default: '' },
    labelColor: { type: String, default: '#52525b' },
    fontSize: { type: Number, default: 11 },
    xLabel: { type: String, default: '' },
    yLabel: { type: String, default: '' },
});

const area = computed(() => getPlotArea(props.size, props.padding));
const resolvedXTicks = computed(() => props.xTicks ?? getNiceTicks(props.domain.xMin, props.domain.xMax, props.tickCount));
const resolvedYTicks = computed(() => props.yTicks ?? getNiceTicks(props.domain.yMin, props.domain.yMax, props.tickCount));
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
