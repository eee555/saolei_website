<template>
    <div class="training-scroll">
        <div class="training-frame" :class="outerBorderClass">
            <button type="button" class="training-frame-counters" :class="innerBorderClass" :aria-label="restartLabel" :title="restartLabel" @click="emit('restart')">
                <slot name="remaining" />
                <slot name="time" />
            </button>
            <div :class="innerBorderClass">
                <slot />
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import '@putianyi888/vue3-minesweeper-board/style.css';

import { innerBorderClass, outerBorderClass } from '@putianyi888/vue3-minesweeper-board';

import { useRestartHotkey } from '@/utils/minigame/settings';

defineProps({ restartLabel: { type: String, required: true } });
const emit = defineEmits<{ restart: [] }>();
useRestartHotkey(() => {
    emit('restart');
});

defineSlots<{
    remaining: () => unknown;
    time: () => unknown;
    default: () => unknown;
}>();
</script>
