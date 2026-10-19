<template>
    <svg ref="svg" v-bind="$attrs" class="board-event-layer" :width="columns * cellSize" :height="rows * cellSize" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" @pointerleave="hideTooltip">
        <g v-for="event in geometry" :key="event.definition.key" class="board-event-layer__event" :data-event-key="event.definition.key">
            <EventMarker v-for="(point, index) in event.pulses" :key="`pulse-${index}`" class="board-event-layer__pulse" :x="point.x * cellSize" :y="point.y * cellSize" :color="event.definition.color" :marker="event.definition.marker" @pointerenter="showTooltip({ key: event.definition.key, type: 'pulse', pulse: point.pulse }, $event)" @pointermove="moveTooltip" @pointerleave="hideTooltip" />
            <g v-for="(path, index) in event.paths" :key="`path-${index}`" class="board-event-layer__span" :opacity="event.definition.line.opacity" :stroke="event.definition.color" @pointerenter="showTooltip({ key: event.definition.key, type: 'sustained', span: path.span }, $event)" @pointermove="moveTooltip" @pointerleave="hideTooltip">
                <polyline class="board-event-layer__path" :points="path.coordinates" fill="none" :stroke-width="event.definition.line.width" :stroke-dasharray="eventLineDash(event.definition.line.style)" />
                <g v-for="(arrow, arrowIndex) in path.arrows" :key="arrowIndex" class="board-event-layer__arrow" :transform="`translate(${arrow.x}, ${arrow.y}) rotate(${arrow.angle})`">
                    <path v-if="settings.arrowShape === 'open'" :d="`M${-settings.arrowSize},${-settings.arrowSize / 2} L0,0 L${-settings.arrowSize},${settings.arrowSize / 2}`" fill="none" :stroke-width="event.definition.line.width" />
                    <path v-else :d="`M0,0 L${-settings.arrowSize},${-settings.arrowSize / 2} L${-settings.arrowSize},${settings.arrowSize / 2} Z`" :fill="event.definition.color" stroke="none" />
                </g>
                <polyline class="board-event-layer__hit-path" :points="path.coordinates" fill="none" stroke="transparent" :stroke-width="Math.max(8, event.definition.line.width)" />
                <circle v-if="path.stationary" class="board-event-layer__hit-point" :cx="path.points[0].x" :cy="path.points[0].y" :r="Math.max(4, event.definition.line.width / 2)" fill="transparent" stroke="none" />
            </g>
        </g>
    </svg>
    <div hidden>
        <div ref="tooltip" class="board-event-layer__tooltip">
            <EventTooltipContent :event="hovered" />
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, useTemplateRef, watch } from 'vue';
import type { PropType } from 'vue';

import { boardEventGeometry, eventDirectionArrows } from './boardEvents';
import type { BoardEventSettings } from './boardEvents';
import { eventLineDash } from './customEvents';
import type { CustomEventDefinition, PreparedCustomEvent } from './customEvents';
import EventMarker from './EventMarker.vue';
import EventTooltipContent from './EventTooltipContent.vue';
import type { ReplayMouseTraceEvent } from './mouseTrace';
import { useEventTooltip } from './useEventTooltip';

const props = defineProps({
    definitions: { type: Array as PropType<CustomEventDefinition[]>, required: true },
    prepared: { type: Object as PropType<Map<string, PreparedCustomEvent>>, required: true },
    mouseEvents: { type: Array as PropType<ReplayMouseTraceEvent[]>, required: true },
    settings: { type: Object as PropType<BoardEventSettings>, required: true },
    currentMs: { type: Number, required: true },
    currentEventIndex: { type: Number as PropType<number | null>, default: null },
    cellSize: { type: Number, required: true },
    rows: { type: Number, required: true },
    columns: { type: Number, required: true },
});
defineOptions({ inheritAttrs: false });
const geometry = computed(() => {
    const past = props.settings.timeRange === 'past';
    return boardEventGeometry(props.definitions, props.prepared, props.mouseEvents, props.settings.keys, past ? props.currentMs : Infinity, past ? props.currentEventIndex : null).map((event) => ({
        ...event,
        paths: event.paths.map((path) => {
            const points = path.points.map((point) => ({ x: point.x * props.cellSize, y: point.y * props.cellSize }));
            const coordinates = points.map((point) => `${point.x},${point.y}`).join(' ');
            const stationary = points.every((point) => point.x === points[0].x && point.y === points[0].y);
            return { points, coordinates, stationary, span: path.span, arrows: eventDirectionArrows(points, props.settings.arrowSpacing) };
        }),
    }));
});

const svg = useTemplateRef<SVGSVGElement>('svg');
const tooltip = useTemplateRef<HTMLDivElement>('tooltip');
const { hovered, showTooltip, moveTooltip, hideTooltip } = useEventTooltip(svg, tooltip);
watch(geometry, (events) => {
    const selected = hovered.value;
    if (selected === null) return;
    const event = events.find((item) => item.definition.key === selected.key);
    const exists = selected.type === 'pulse' ? event?.pulses.some((point) => point.pulse === selected.pulse) : event?.paths.some((path) => path.span === selected.span);
    if (exists !== true) hideTooltip();
});
watch([() => props.cellSize, () => props.rows, () => props.columns], hideTooltip);
</script>

<style scoped>
.board-event-layer {
    position: absolute;
    inset: 0;
    z-index: 4;
    pointer-events: none;
    overflow: hidden;
}

.board-event-layer__pulse,
.board-event-layer__span {
    pointer-events: visiblePainted;
    cursor: help;
}

.board-event-layer__hit-path {
    pointer-events: stroke;
}

.board-event-layer__hit-point {
    pointer-events: all;
}
</style>
