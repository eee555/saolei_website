<template>
    <el-row style="height: 1px" />
    <el-row>
        <span style="flex: 1" />
        <el-col :span="10" style="min-width: 16em">
            <LevelBlock level="b" :videos="videos" />
        </el-col>
        <span style="flex: 1" />
        <el-col :span="10" style="min-width: 16em">
            <LevelBlock level="i" :videos="videos" />
            <el-row style="height: 25px" />
            <LevelBlock level="e" :videos="videos" />
        </el-col>
        <span style="flex: 1" />
    </el-row>
    <el-row style="height: 1px" />
</template>

<script setup lang="ts">

import { PropType } from 'vue';
import LevelBlock from './LevelBlock.vue';
import { VideoAbstract } from '@/utils/videoabstract';
import { ElRow, ElCol } from 'element-plus';

defineProps({
    videos: {
        type: Array as PropType<VideoAbstract[]>,
        default: () => [],
    },
});

</script>

<style lang="less" scoped>

.levelblock {
    width: 30%;
    display: inline-block;
    vertical-align: top;
    min-width: 16em;
}

</style>
