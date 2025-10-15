<template>
    <div>
        <el-col :span="6" style="display: inline-block; width: 25%">
            <HeadColumn :level="level" :count="defaultCounts[level]" />
        </el-col>
        <el-col :span="6" style="display: inline-block; width: 25%">
            <SortedColumn ref="timeColumnRef" :level="level" :count="defaultCounts[level]" :videos="filteredVideos.filter((video) => video.time() < defaultVideos[level].time)" sort-by="time" />
        </el-col>
        <el-col :span="6" style="display: inline-block; width: 25%">
            <SortedColumn ref="bvsColumnRef" :level="level" :count="defaultCounts[level]" :videos="filteredVideos" sort-by="bvs" />
        </el-col>
        <el-col :span="6" style="display: inline-block; width: 25%">
            <SortedColumn ref="stnbColumnRef" :level="level" :count="defaultCounts[level]" :videos="filteredVideos" sort-by="stnb" />
        </el-col>
    </div>
</template>

<script setup lang="ts">
import { MS_Level, MS_State } from '@/utils/ms_const';
import { computed, PropType, ref } from 'vue';
import HeadColumn from './HeadColumn.vue';
import { defaultCounts, defaultVideos } from './utils';
import SortedColumn from './SortedColumn.vue';
import { VideoAbstract } from '@/utils/videoabstract';
import { ElCol } from 'element-plus';


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

const timeColumnRef = ref<InstanceType<typeof SortedColumn>>();
const bvsColumnRef = ref<InstanceType<typeof SortedColumn>>();
const stnbColumnRef = ref<InstanceType<typeof SortedColumn>>();

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
        time: timeColumnRef.value?.sumStat || defaultVideos[props.level].time * defaultCounts[props.level],
        bvs: bvsColumnRef.value?.sumStat || defaultVideos[props.level].bvs * defaultCounts[props.level],
        stnb: stnbColumnRef.value?.sumStat || defaultVideos[props.level].stnb * defaultCounts[props.level],
    };
});

defineExpose({
    sumAll,
});

</script>
