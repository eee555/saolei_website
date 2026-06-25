<template>
    <div>
        <ElCol :span="6" style="display: inline-block; width: 25%">
            <HeadColumn :level="level" :count="defaultCounts[level]" />
        </ElCol>
        <ElCol :span="6" style="display: inline-block; width: 25%">
            <SortedColumn ref="timeColumnRef" :level="level" :count="defaultCounts[level]" :videos="filteredVideos.filter((video) => video.time < defaultVideos[level].time)" sort-by="time" />
        </ElCol>
        <ElCol :span="6" style="display: inline-block; width: 25%">
            <SortedColumn ref="bvsColumnRef" :level="level" :count="defaultCounts[level]" :videos="filteredVideos" sort-by="bvs" />
        </ElCol>
        <ElCol :span="6" style="display: inline-block; width: 25%">
            <SortedColumn ref="stnbColumnRef" :level="level" :count="defaultCounts[level]" :videos="filteredVideos" sort-by="stnb" />
        </ElCol>
    </div>
</template>

<script setup lang="ts">
import { ElCol } from 'element-plus';
import type { PropType } from 'vue';
import { computed, useTemplateRef } from 'vue';

import HeadColumn from './HeadColumn.vue';
import SortedColumn from './SortedColumn.vue';
import { defaultCounts, defaultVideos } from './utils';

import type { MS_Level } from '@/utils/ms_const';
import { MS_State } from '@/utils/ms_const';
import type { VideoAbstract } from '@/utils/videoabstract';

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

function isValid(video: VideoAbstract) {
    if (video.level != props.level || video.state != MS_State.Official) return false;
    if (video.level === 'b' && video.bv < 10) return false;
    return true;
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
