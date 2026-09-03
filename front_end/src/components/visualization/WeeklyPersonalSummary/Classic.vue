<template>
    <div class="text text-large">
        {{ t('common.level.sum') }}{{ t('common.punct.colon') }}{{ ms_to_s(iSum + eSum) }}
    </div>
    <div class="text text-large" style="margin-top: 0.5em">
        {{ t('common.level.e') }}{{ t('common.punct.colon') }}{{ ms_to_s(eSum) }}
    </div>
    <div class="cell-list">
        <Cell :video="bestE[0]" :color-theme="colorSchemeE" :default-time="240" />
        <Cell :video="bestE[1]" :color-theme="colorSchemeE" :default-time="240" />
    </div>
    <div class="text text-large" style="margin-top: 0.5em">
        {{ t('common.level.i') }}{{ t('common.punct.colon') }}{{ ms_to_s(iSum) }}
    </div>
    <div class="cell-list">
        <Cell :video="bestI[0]" :color-theme="colorSchemeI" :default-time="60" />
        <Cell :video="bestI[1]" :color-theme="colorSchemeI" :default-time="60" />
        <Cell :video="bestI[2]" :color-theme="colorSchemeI" :default-time="60" />
        <Cell :video="bestI[3]" :color-theme="colorSchemeI" :default-time="60" />
        <Cell :video="bestI[4]" :color-theme="colorSchemeI" :default-time="60" />
    </div>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

import Cell from './Cell.vue';

import { colorTheme } from '@/store';
import { ms_to_s } from '@/utils';
import { PiecewiseColorScheme } from '@/utils/colors';
import type { VideoAbstract } from '@/utils/videoabstract';
import { isWeeklyClassicScoreMode } from '@/utils/weekly';

const props = defineProps({
    videos: { type: Array<VideoAbstract>, default: () => [] },
});

const { t } = useI18n();

const colorSchemeI = computed(() => PiecewiseColorScheme.createFromTheme(colorTheme.value.itime));
const colorSchemeE = computed(() => PiecewiseColorScheme.createFromTheme(colorTheme.value.etime));

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
