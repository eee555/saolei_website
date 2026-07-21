<template>
    <div class="player-main" :class="outerBorderClass">
        <div class="player-main__counter-bar" :class="innerBorderClass">
            <Counter :value="video.mine_num - video.flag" :digits="3" :size="18" />
            <span class="player-main__counter-spacer" />
            <InputNumber
                v-model="boardSize"
                class="player-main__size-input"
                :min="1" :max="48"
                :title="t('local.size')"
            />
            <span class="player-main__counter-spacer" />
            <Counter :value="currentMs / 1000" :fixed="3" :digits="3" :size="18" />
        </div>
        <div :class="innerBorderClass">
            <MinesweeperBoard :board="video.game_board" :size="boardSize" :cursor-position="cursorPosition" />
        </div>
    </div>
</template>

<script setup lang="ts">
import '@putianyi888/vue3-minesweeper-board/style.css';

import { Counter, innerBorderClass, MinesweeperBoard, outerBorderClass } from '@putianyi888/vue3-minesweeper-board';
import type { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import InputNumber from '@/components/common/InputNumber.vue';
import type { AnyVideo } from '@/utils/fileIO';

interface CursorPosition {
    rowIndex: number;
    columnIndex: number;
}

defineProps({
    video: { type: Object as PropType<AnyVideo>, required: true },
    currentMs: { type: Number, required: true },
    cursorPosition: { type: Object as PropType<CursorPosition>, default: undefined },
});

const boardSize = defineModel<number>('boardSize', { default: 16 });

const i18nMessages = {
    'zh-cn': { local: {
        size: '格子边长',
    } },
    en: { local: {
        size: 'Cell size',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
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
    align-items: center;
    align-self: stretch;
    gap: 4px;
}

.player-main__counter-spacer {
    flex: 1 1 0;
    min-width: 0;
}

.player-main__size-input {
    width: 44px;
}
</style>
