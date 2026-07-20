<template>
    <div class="native-player__board-frame player-main" :class="outerBorderClass">
        <div class="player-main__counter-bar" :class="innerBorderClass">
            <Counter :value="video.mine_num - video.flag" :digits="3" :size="18" />
            <span class="player-main__counter-spacer" />
            <Counter :value="currentMs / 1000" :fixed="3" :digits="3" :size="18" />
        </div>
        <div class="player-main__board-wrap" :class="innerBorderClass" :style="boardWrapStyle">
            <MinesweeperBoard :board="board" :size="boardSize" :cursor-position="cursorPosition" />
        </div>
    </div>
</template>

<script setup lang="ts">
import '@putianyi888/vue3-minesweeper-board/style.css';

import { Counter, innerBorderClass, MinesweeperBoard, outerBorderClass } from '@putianyi888/vue3-minesweeper-board';
import type { PropType } from 'vue';
import { computed } from 'vue';

import type { AnyVideo } from '@/utils/fileIO';

interface CursorPosition {
    rowIndex: number;
    columnIndex: number;
}

const props = defineProps({
    video: { type: Object as PropType<AnyVideo>, required: true },
    board: { type: Array as PropType<number[][]>, required: true },
    boardSize: { type: Number, required: true },
    currentMs: { type: Number, required: true },
    cursorPosition: { type: Object as PropType<CursorPosition>, default: undefined },
});

const boardWrapStyle = computed(() => ({
    height: `${Math.max(1, props.video.row) * props.boardSize}px`,
    width: `${Math.max(1, props.video.column) * props.boardSize}px`,
}));
</script>

<style scoped>
.player-main {
    display: flex;
    flex: 0 0 auto;
    flex-direction: column;
}

.player-main__counter-bar {
    display: flex;
    flex-direction: row;
    align-self: stretch;
}

.player-main__counter-spacer {
    flex-grow: 1;
}

.player-main__board-wrap {
    position: relative;
    overflow: hidden;
    flex: 0 0 auto;
}
</style>
