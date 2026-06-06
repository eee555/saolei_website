<template>
    <svg
        class="plot-scatter"
        :height="size.height" :width="size.width"
        :viewBox="`0 0 ${size.width} ${size.height}`"
        preserveAspectRatio="none"
    >
        <circle
            v-for="(point, index) in renderedPoints" :key="index" class="plot-scatter__point"
            :cx="point.x" :cy="point.y" :fill="fill" :r="radius"
            :stroke="stroke" :stroke-width="strokeWidth"
            vector-effect="non-scaling-stroke"
            @click="emit('point-click', point.data)"
            @mouseenter="emit('point-enter', point.data)"
            @mouseleave="emit('point-leave', point.data)"
        />
    </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { PropType } from 'vue';

import { defaultPlotPadding, getPlotArea, pointToSvg } from './utils';
import type { PlotDomain, PlotPadding, PlotPoint, PlotSize } from './utils';

const props = defineProps({
    points: { type: Array as PropType<PlotPoint[]>, required: true },
    domain: { type: Object as PropType<PlotDomain>, required: true },
    size: { type: Object as PropType<PlotSize>, default: () => ({ width: 320, height: 200 }) },
    padding: { type: Object as PropType<PlotPadding>, default: () => defaultPlotPadding },
    radius: { type: Number, default: 3 },
    fill: { type: String, default: '#2563eb' },
    stroke: { type: String, default: 'none' },
    strokeWidth: { type: Number, default: 0 },
});

const emit = defineEmits<{
    'point-click': [point: PlotPoint];
    'point-enter': [point: PlotPoint];
    'point-leave': [point: PlotPoint];
}>();

const renderedPoints = computed(() => {
    const area = getPlotArea(props.size, props.padding);

    return props.points.
        filter((point) => Number.isFinite(point.x) && Number.isFinite(point.y)).
        map((point) => ({
            ...pointToSvg(point, props.domain, area),
            data: point,
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
