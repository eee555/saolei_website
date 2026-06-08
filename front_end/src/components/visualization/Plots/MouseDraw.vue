<template>
    <svg
        class="plot-mouse-draw"
        :class="{ 'plot-mouse-draw--disabled': !isEnabled }"
        :height="size.height" :width="size.width"
        :viewBox="`0 0 ${size.width} ${size.height}`"
        preserveAspectRatio="none"
        @click.stop.prevent
        @dblclick.stop.prevent
        @mousedown.stop.prevent="startDraw"
        @mouseenter.stop
        @mouseleave.stop.prevent="finishDraw"
        @mousemove.stop.prevent="moveDraw"
        @mouseup.stop.prevent="finishDraw"
    >
        <rect
            v-if="drawingShape?.type === 'rect'"
            class="plot-mouse-draw__shape"
            :height="drawingShape.height" :width="drawingShape.width"
            :x="drawingShape.x" :y="drawingShape.y"
            vector-effect="non-scaling-stroke"
        />
        <ellipse
            v-else-if="drawingShape?.type === 'ellipse'"
            class="plot-mouse-draw__shape"
            :cx="drawingShape.cx" :cy="drawingShape.cy"
            :rx="drawingShape.rx" :ry="drawingShape.ry"
            vector-effect="non-scaling-stroke"
        />
    </svg>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import type { PropType } from 'vue';

import { Ellipse, Rect } from './geometry';
import type { AnyShape, Point } from './geometry';
import type { PlotSize } from './utils';

type MouseDrawMode = '' | 'rect' | 'ellipse';

const props = defineProps({
    mode: { type: String as PropType<MouseDrawMode>, default: 'rect' },
    size: { type: Object as PropType<PlotSize>, default: () => ({ width: 320, height: 200 }) },
});

const emit = defineEmits<{
    (e: 'draw', shape: AnyShape): void;
}>();

const isEnabled = computed(() => props.mode !== '');
const startPoint = ref<Point>();
const drawingShape = ref<AnyShape>();

watch(() => props.mode, (mode) => {
    if (mode === '') clearDraw();
});

function startDraw(event: MouseEvent) {
    if (!isEnabled.value) return;

    startPoint.value = getSvgPoint(event);
    drawingShape.value = createShape(startPoint.value, startPoint.value);
}

function moveDraw(event: MouseEvent) {
    if (!isEnabled.value || startPoint.value === undefined) return;

    drawingShape.value = createShape(startPoint.value, getSvgPoint(event));
}

function finishDraw(event: MouseEvent) {
    if (!isEnabled.value || startPoint.value === undefined) return;

    const shape = createShape(startPoint.value, getSvgPoint(event));
    emit('draw', shape);
    clearDraw();
}

function clearDraw() {
    startPoint.value = undefined;
    drawingShape.value = undefined;
}

function createShape(start: Point, end: Point): AnyShape {
    if (props.mode === 'ellipse') return createEllipse(start, end);
    if (props.mode === 'rect') return createRect(start, end);

    throw new Error('MouseDraw is disabled.');
}

function createRect(start: Point, end: Point): Rect {
    const x = Math.min(start.x, end.x);
    const y = Math.min(start.y, end.y);

    return new Rect(x, y, Math.abs(end.x - start.x), Math.abs(end.y - start.y));
}

function createEllipse(start: Point, end: Point): Ellipse {
    const rect = createRect(start, end);

    return new Ellipse(rect.x + rect.width / 2, rect.y + rect.height / 2, rect.width / 2, rect.height / 2);
}

function getSvgPoint(event: MouseEvent): Point {
    const rect = (event.currentTarget as SVGSVGElement).getBoundingClientRect();
    const scaleX = rect.width === 0 ? 1 : props.size.width / rect.width;
    const scaleY = rect.height === 0 ? 1 : props.size.height / rect.height;

    return {
        x: (event.clientX - rect.left) * scaleX,
        y: (event.clientY - rect.top) * scaleY,
    };
}
</script>

<style lang="less" scoped>
.plot-mouse-draw {
    display: block;
    height: 100%;
    inset: 0;
    overflow: hidden;
    pointer-events: auto;
    position: absolute;
    width: 100%;
}

.plot-mouse-draw--disabled {
    pointer-events: none;
}

.plot-mouse-draw__shape {
    fill: rgb(37 99 235 / 12%);
    stroke: currentcolor;
    stroke-width: 1;
}
</style>
