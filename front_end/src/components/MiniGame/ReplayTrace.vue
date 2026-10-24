<template>
    <MouseTrace class="minigame-replay-trace" :events="replay.events" :start-index="0" :end-index="eventIndex + 1" v-bind="minigameReplayAppearance" />
</template>

<script setup lang="ts">
import { MouseTrace } from '@putianyi888/vue3-minesweeper-board';
import type { PropType } from 'vue';

import { minigameReplayAppearance } from '@/utils/minigame/replay';
import type { TrainingReplay } from '@/utils/minigame/replay';

defineProps({ replay: { type: Object as PropType<TrainingReplay>, required: true }, eventIndex: { type: Number, required: true } });
</script>

<style scoped>
.minigame-replay-trace {
    pointer-events: none;
}
</style>
