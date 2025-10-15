<template>
    <div>
        <el-col :span="6" style="display: inline-block; width: 25%">
            <HeadColumn :level="level" :count="defaultCounts[level]" />
        </el-col>
        <el-col :span="6" style="display: inline-block; width: 25%">
            <SortedColumn :level="level" :count="defaultCounts[level]" :videos="filteredVideos" sort-by="time" />
        </el-col>
        <el-col :span="6" style="display: inline-block; width: 25%">
            <SortedColumn :level="level" :count="defaultCounts[level]" :videos="filteredVideos" sort-by="bvs" />
        </el-col>
        <el-col :span="6" style="display: inline-block; width: 25%">
            <SortedColumn :level="level" :count="defaultCounts[level]" :videos="filteredVideos" sort-by="stnb" />
        </el-col>
    </div>
</template>

<script setup lang="ts">
import { MS_Level, MS_State } from '@/utils/ms_const';
import { computed, PropType } from 'vue';
import HeadColumn from './HeadColumn.vue';
import { defaultCounts } from './utils';
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

const filteredVideos = computed(() => {
    return props.videos.filter((video) => video.level === props.level && video.state === MS_State.Official);
});

</script>
