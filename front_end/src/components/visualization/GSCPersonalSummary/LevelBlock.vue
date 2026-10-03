<template>
    <div>
        <div class="summary-column">
            <HeadColumn :level="level" :count="defaultCounts[level]" />
        </div>
        <div class="summary-column">
            <SortedColumn ref="timeColumnRef" :level="level" :count="defaultCounts[level]" :videos="filteredVideos.filter((video) => video.time < defaultVideos[level].time)" sort-by="time" />
        </div>
        <div class="summary-column">
            <SortedColumn ref="bvsColumnRef" :level="level" :count="defaultCounts[level]" :videos="filteredVideos" sort-by="bvs" />
        </div>
        <div class="summary-column">
            <SortedColumn ref="stnbColumnRef" :level="level" :count="defaultCounts[level]" :videos="filteredVideos" sort-by="stnb" />
        </div>
    </div>
</template>

<script setup lang="ts">
import type { PropType } from 'vue';
import { computed, useTemplateRef } from 'vue';

import HeadColumn from './HeadColumn.vue';
import SortedColumn from './SortedColumn.vue';
import { defaultCounts, defaultVideos } from './utils';

import { isGSCSupportedVideo, meetsGSCBV } from '@/utils/gsc';
import type { MS_Level } from '@/utils/ms_const';
import { MS_State } from '@/utils/ms_const';
import type { StandardVideoAbstract, VideoAbstract } from '@/utils/videoabstract';

const props = defineProps({
    videos: {
        type: Array as PropType<VideoAbstract[]>,
        default: () => [],
    },
    level: {
        type: String as PropType<MS_Level>,
        required: true,
    },
});

const timeColumnRef = useTemplateRef('timeColumnRef');
const bvsColumnRef = useTemplateRef('bvsColumnRef');
const stnbColumnRef = useTemplateRef('stnbColumnRef');

function isValid(video: VideoAbstract): video is StandardVideoAbstract {
    if (video.level != props.level || video.state != MS_State.Official) return false;
    return isGSCSupportedVideo(video) && meetsGSCBV(video);
}

const filteredVideos = computed(() => {
    return props.videos.filter(isValid);
});

const sumAll = computed(() => {
    return {
        time: timeColumnRef.value?.sumStat ?? defaultVideos[props.level].time * defaultCounts[props.level],
        bvs: bvsColumnRef.value?.sumStat ?? defaultVideos[props.level].bvs * defaultCounts[props.level],
        stnb: stnbColumnRef.value?.sumStat ?? defaultVideos[props.level].stnb * defaultCounts[props.level],
    };
});

defineExpose({
    sumAll,
});
</script>

<style scoped>
.summary-column {
    box-sizing: border-box;
    display: inline-block;
    vertical-align: top;
    width: 25%;
}
</style>
