<template>
    <svg class="board-event-layer" :width="columns * cellSize" :height="rows * cellSize" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <g v-for="event in geometry" :key="event.definition.key" class="board-event-layer__event">
            <EventMarker v-for="(point, index) in event.pulses" :key="`pulse-${index}`" class="board-event-layer__pulse" :x="point.x * cellSize" :y="point.y * cellSize" :color="event.definition.color" :marker="event.definition.marker" />
            <g v-for="(path, index) in event.paths" :key="`path-${index}`" :opacity="event.definition.line.opacity" :stroke="event.definition.color">
                <polyline class="board-event-layer__path" :points="path.points.map((point) => `${point.x},${point.y}`).join(' ')" fill="none" :stroke-width="event.definition.line.width" :stroke-dasharray="eventLineDash(event.definition.line.style)" />
                <g v-for="(arrow, arrowIndex) in path.arrows" :key="arrowIndex" class="board-event-layer__arrow" :transform="`translate(${arrow.x}, ${arrow.y}) rotate(${arrow.angle})`">
                    <path v-if="settings.arrowShape === 'open'" :d="`M${-settings.arrowSize},${-settings.arrowSize / 2} L0,0 L${-settings.arrowSize},${settings.arrowSize / 2}`" fill="none" :stroke-width="event.definition.line.width" />
                    <path v-else :d="`M0,0 L${-settings.arrowSize},${-settings.arrowSize / 2} L${-settings.arrowSize},${settings.arrowSize / 2} Z`" :fill="event.definition.color" stroke="none" />
                </g>
            </g>
        </g>
    </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { PropType } from 'vue';

import { boardEventGeometry, eventDirectionArrows } from './boardEvents';
import type { BoardEventSettings } from './boardEvents';
import { eventLineDash } from './customEvents';
import type { CustomEventDefinition, PreparedCustomEvent } from './customEvents';
import EventMarker from './EventMarker.vue';
import type { ReplayMouseTraceEvent } from './mouseTrace';

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
const geometry = computed(() => {
    const past = props.settings.timeRange === 'past';
    return boardEventGeometry(props.definitions, props.prepared, props.mouseEvents, props.settings.keys, past ? props.currentMs : Infinity, past ? props.currentEventIndex : null).map((event) => ({
        ...event,
        paths: event.paths.map((path) => {
            const points = path.map((point) => ({ x: point.x * props.cellSize, y: point.y * props.cellSize }));
            return { points, arrows: eventDirectionArrows(points, props.settings.arrowSpacing) };
        }),
    }));
});
</script>

<style scoped>
.board-event-layer {
    position: absolute;
    inset: 0;
    z-index: 4;
    pointer-events: none;
    overflow: hidden;
}
</style>
