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

        <g v-for="tick in resolvedXTicks" :key="`x-${tick}`" class="plot-axes__tick">
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

        <g v-for="tick in resolvedYTicks" :key="`y-${tick}`" class="plot-axes__tick">
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

import { createLinearScale, defaultPlotPadding, formatTick, getNiceTicks, getPlotArea } from './utils';
import type { PlotDomain, PlotPadding, PlotSize } from './utils';

defineSlots<{
    'x-tick': (props: { tick: number; x: number; y: number }) => unknown;
    'y-tick': (props: { tick: number; x: number; y: number }) => unknown;
}>();

const props = defineProps({
    domain: { type: Object as PropType<PlotDomain>, required: true },
    size: { type: Object as PropType<PlotSize>, default: () => ({ width: 320, height: 200 }) },
    padding: { type: Object as PropType<PlotPadding>, default: () => defaultPlotPadding },
    xTicks: { type: Array as PropType<number[]>, default: undefined },
    yTicks: { type: Array as PropType<number[]>, default: undefined },
    tickCount: { type: Number, default: 5 },
    tickSize: { type: Number, default: 4 },
    stroke: { type: String, default: '#71717a' },
    strokeWidth: { type: Number, default: 1 },
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
