<template>
    <div v-show="position !== null" class="board-cursor-layer" :style="{ left: `${(position?.columnIndex ?? 0) * cellSize}px`, top: `${(position?.rowIndex ?? 0) * cellSize}px` }" aria-hidden="true">
        <svg ref="svg" class="board-cursor-layer__svg" :class="{ 'board-cursor-layer__svg--windows': shape === 'windows' }" :style="{ transform: `translate(${-anchor.x * 100}%, ${-anchor.y * 100}%)` }" :width="size" :height="size" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle v-if="shape === 'dot'" class="board-cursor-layer__dot" cx="16" cy="16" r="3" fill="#ffdf00" stroke="#222" stroke-width="1.5" />
            <path v-else-if="shape === 'windows'" class="board-cursor-layer__windows" d="M3 2V24L8.5 18.5L12.5 28L17 26L13 17H22Z" fill="white" stroke="#222" stroke-width="1.5" stroke-linejoin="round" />
            <template v-else-if="shape === 'ring'">
                <circle cx="16" cy="16" r="9" fill="none" stroke="white" stroke-width="3.5" />
                <circle cx="16" cy="16" r="9" fill="none" stroke="#222" stroke-width="1.5" />
            </template>
            <template v-else-if="shape === 'crosshair'">
                <path d="M16 4V28M4 16H28" stroke="white" stroke-width="3.5" />
                <path d="M16 4V28M4 16H28" stroke="#222" stroke-width="1.5" />
            </template>
        </svg>
    </div>
</template>

<script setup lang="ts">
import { computed, useTemplateRef } from 'vue';
import type { PropType } from 'vue';

import type { ExportCursor } from './boardExportFrame';
import type { CursorShape } from './config';
import type { CursorPosition } from './useReplayPosition';

const props = defineProps({
    position: { type: Object as PropType<CursorPosition | null>, default: null },
    cellSize: { type: Number, required: true },
    shape: { type: String as PropType<CursorShape>, required: true },
    size: { type: Number, required: true },
});
const svg = useTemplateRef('svg');
const anchor = computed(() => (props.shape === 'windows' ? { x: 3 / 32, y: 2 / 32 } : { x: 0.5, y: 0.5 }));
function snapshot(position = props.position, cellSize = props.cellSize): ExportCursor | null {
    if (position === null || svg.value === null) return null;
    return { svg: svg.value,
        x: position.columnIndex * cellSize - props.size * anchor.value.x,
        y: position.rowIndex * cellSize - props.size * anchor.value.y,
        size: props.size };
}
defineExpose({ snapshot });
</script>

<style scoped>
.board-cursor-layer {
    position: absolute;
    width: 0;
    height: 0;
    z-index: 5;
    pointer-events: none;
}

.board-cursor-layer__svg {
    display: block;
    max-width: none;
}
</style>
