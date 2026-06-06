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
            @click="console.log('point-click'); emit('point-click', point.source)"
            @mouseenter="emit('point-enter', point.source)"
            @mouseleave="emit('point-leave', point.source)"
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
    fill: { type: String, default: '#2563eb' },
    // Circle outline color. Use "none" to hide the outline.
    stroke: { type: String, default: 'none' },
    // Circle outline width in pixels.
    strokeWidth: { type: Number, default: 0 },
});

const emit = defineEmits<{
    (e: 'point-click', point: PlotPoint<T>): void;
    (e: 'point-enter', point: PlotPoint<T>): void;
    (e: 'point-leave', point: PlotPoint<T>): void;
}>();

const renderedPoints = computed(() => {
    const area = getPlotArea(props.size, props.padding);

    return props.points.
        filter((point) => Number.isFinite(point.x) && Number.isFinite(point.y)).
        map((point) => ({
            ...pointToSvg(point, props.domain, area),
            source: point,
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
