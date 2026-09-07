<template>
    <div class="text text-large">
        {{ t('common.level.sum') }}{{ t('common.punct.colon') }}{{ ms_to_s(iSum + eSum) }}
    </div>
    <div class="text text-large" style="margin-top: 0.5em">
        {{ t('common.level.e') }}{{ t('common.punct.colon') }}{{ ms_to_s(eSum) }}
    </div>
    <div class="cell-list">
        <Cell v-for="i in 2" :key="`e${i}`" :video="bestE[i]" :color-theme="colorThemes.etime.value" :default-time="240" />
    </div>
    <div class="text text-large" style="margin-top: 0.5em">
        {{ t('common.level.i') }}{{ t('common.punct.colon') }}{{ ms_to_s(iSum) }}
    </div>
    <div class="cell-list">
        <Cell v-for="i in 5" :key="`i${i}`" :video="bestI[i]" :color-theme="colorThemes.itime.value" :default-time="60" />
    </div>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

import Cell from './Cell.vue';

import { colorThemes } from '@/store/color';
import { ms_to_s } from '@/utils';
import type { VideoAbstract } from '@/utils/videoabstract';
import { isWeeklyClassicScoreMode } from '@/utils/weekly';

const props = defineProps({
    videos: { type: Array<VideoAbstract>, default: () => [] },
});

const { t } = useI18n();

function bestVideos(videos: VideoAbstract[], level: 'i' | 'e') {
    const filtered = videos.filter((video) => video.level === level && isWeeklyClassicScoreMode(video.mode));
    const sorted = filtered.sort((v1, v2) => v1.timems - v2.timems);
    if (level === 'i') return sorted.slice(0, 5);
    return sorted.slice(0, 2);
}

const bestI = computed(() => bestVideos(props.videos, 'i'));
const bestE = computed(() => bestVideos(props.videos, 'e'));

const iSum = computed(() => bestI.value.reduce((sum, video) => sum + video.timems, 0) + 60000 * (5 - bestI.value.length));
const eSum = computed(() => bestE.value.reduce((sum, video) => sum + video.timems, 0) + 240000 * (2 - bestE.value.length));
</script>

<style scoped>
.cell-list {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
}
</style>
