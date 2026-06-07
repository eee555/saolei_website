<template>
    <svg
        class="plot-axes"
        :height="size.height" :width="size.width"
        :viewBox="`0 0 ${size.width} ${size.height}`"
        preserveAspectRatio="none"
    >
        <line
            :stroke="stroke" :stroke-width="strokeWidth"
            :x1="area.x" :x2="area.x + area.width"
            :y1="area.y + area.height" :y2="area.y + area.height"
            vector-effect="non-scaling-stroke"
        />
        <line
            :stroke="stroke" :stroke-width="strokeWidth"
            :x1="area.x" :x2="area.x"
            :y1="area.y" :y2="area.y + area.height"
            vector-effect="non-scaling-stroke"
        />

        <g v-for="tick in xTicks" :key="`x-${tick}`" class="plot-axes__tick">
            <line
                :stroke="stroke" :stroke-width="strokeWidth"
                :x1="xScale(tick)" :x2="xScale(tick)"
                :y1="area.y + area.height" :y2="area.y + area.height + tickSize"
                vector-effect="non-scaling-stroke"
            />
            <text
                :fill="labelColor" :font-size="fontSize"
                :x="xScale(tick)" :y="area.y + area.height + tickSize + fontSize"
                text-anchor="middle"
            >
                <slot
                    name="x-tick" :tick="tick"
                    :x="xScale(tick)" :y="area.y + area.height + tickSize + fontSize"
                >
                    {{ formatTick(tick) }}
                </slot>
            </text>
        </g>

        <g v-for="tick in yTicks" :key="`y-${tick}`" class="plot-axes__tick">
            <line
                :stroke="stroke" :stroke-width="strokeWidth"
                :x1="area.x - tickSize" :x2="area.x"
                :y1="yScale(tick)" :y2="yScale(tick)"
                vector-effect="non-scaling-stroke"
            />
            <text
                :fill="labelColor" :font-size="fontSize"
                :x="area.x - tickSize - 4" :y="yScale(tick)"
                dominant-baseline="middle" text-anchor="end"
            >
                <slot
                    name="y-tick" :tick="tick"
                    :x="area.x - tickSize - 4" :y="yScale(tick)"
                >
                    {{ formatTick(tick) }}
                </slot>
            </text>
        </g>

        <text
            v-if="xLabel" :fill="labelColor" :font-size="fontSize"
            :x="area.x + area.width / 2" :y="size.height - 2"
            text-anchor="middle"
        >
            {{ xLabel }}
        </text>
        <text
            v-if="yLabel" :fill="labelColor" :font-size="fontSize"
            :transform="`translate(${fontSize}, ${area.y + area.height / 2}) rotate(-90)`"
            text-anchor="middle"
        >
            {{ yLabel }}
        </text>
    </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { PropType } from 'vue';

import { createLinearScale, defaultPlotPadding, formatTick, getPlotArea } from './utils';
import type { PlotDomain, PlotPadding, PlotSize } from './utils';

defineSlots<{
    'x-tick': (props: { tick: number; x: number; y: number }) => unknown;
    'y-tick': (props: { tick: number; x: number; y: number }) => unknown;
}>();

const props = defineProps({
    // Data-space bounds used to map values onto the plot area.
    domain: { type: Object as PropType<PlotDomain>, required: true },
    // Outer SVG size in pixels. Parent components usually provide this from ResizeObserver.
    size: { type: Object as PropType<PlotSize>, default: () => ({ width: 320, height: 200 }) },
    // Insets reserved inside the SVG for labels, ticks, and axis titles.
    padding: { type: Object as PropType<PlotPadding>, default: () => defaultPlotPadding },
    // X-axis tick values in data-space coordinates.
    xTicks: { type: Array as PropType<number[]>, default: () => [] },
    // Y-axis tick values in data-space coordinates.
    yTicks: { type: Array as PropType<number[]>, default: () => [] },
    // Length of tick marks in pixels.
    tickSize: { type: Number, default: 4 },
    // Axis line and tick mark color.
    stroke: { type: String, default: '#71717a' },
    // Axis line and tick mark width in pixels.
    strokeWidth: { type: Number, default: 1 },
    // Tick label and axis title color.
    labelColor: { type: String, default: '#52525b' },
    // Tick label and axis title font size in pixels.
    fontSize: { type: Number, default: 11 },
    // Optional title shown below the x axis.
    xLabel: { type: String, default: '' },
    // Optional title shown along the y axis.
    yLabel: { type: String, default: '' },
});

const area = computed(() => getPlotArea(props.size, props.padding));
const xScale = computed(() => createLinearScale(props.domain.xMin, props.domain.xMax, area.value.x, area.value.x + area.value.width));
const yScale = computed(() => createLinearScale(props.domain.yMin, props.domain.yMax, area.value.y + area.value.height, area.value.y));
</script>

<style lang="less" scoped>
.plot-axes {
    display: block;
    height: 100%;
    inset: 0;
    overflow: visible;
    pointer-events: none;
    position: absolute;
    width: 100%;
}
</style>
