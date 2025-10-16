<template>
    <el-row>
        <AllSums :sum-time="sumTime" :sum-bvs="sumBvs" :sum-stnb="sumStnb" />
    </el-row>
    <el-row style="height: 20px" />
    <el-row>
        <span style="flex: 1" />
        <el-col :span="10" style="min-width: 16em">
            <LevelBlock ref="BBlockRef" level="b" :videos="videos" />
        </el-col>
        <span style="flex: 1" />
        <el-col :span="10" style="min-width: 16em">
            <LevelBlock ref="IBlockRef" level="i" :videos="videos" />
            <el-row style="height: 25px" />
            <LevelBlock ref="EBlockRef" level="e" :videos="videos" />
        </el-col>
        <span style="flex: 1" />
    </el-row>
    <el-row style="height: 20px" />
    <el-row>
        <AllSums :sum-time="sumTime" :sum-bvs="sumBvs" :sum-stnb="sumStnb" />
    </el-row>
</template>

<script setup lang="ts">

import { computed, PropType, ref } from 'vue';
import LevelBlock from './LevelBlock.vue';
import { VideoAbstract } from '@/utils/videoabstract';
import { ElRow, ElCol } from 'element-plus';
import AllSums from './AllSums.vue';

defineProps({
    videos: {
        type: Array as PropType<VideoAbstract[]>,
        default: () => [],
    },
});

const BBlockRef = ref<InstanceType<typeof LevelBlock>>();
const IBlockRef = ref<InstanceType<typeof LevelBlock>>();
const EBlockRef = ref<InstanceType<typeof LevelBlock>>();

const sumTime = computed(() => {
    return (BBlockRef.value ? BBlockRef.value.sumAll.time : 0) + (IBlockRef.value ? IBlockRef.value.sumAll.time : 0) + (EBlockRef.value ? EBlockRef.value.sumAll.time : 0);
});

const sumBvs = computed(() => {
    return (BBlockRef.value ? BBlockRef.value.sumAll.bvs : 0) + (IBlockRef.value ? IBlockRef.value.sumAll.bvs : 0) + (EBlockRef.value ? EBlockRef.value.sumAll.bvs : 0);
});

const sumStnb = computed(() => {
    return (BBlockRef.value ? BBlockRef.value.sumAll.stnb : 0) + (IBlockRef.value ? IBlockRef.value.sumAll.stnb : 0) + (EBlockRef.value ? EBlockRef.value.sumAll.stnb : 0);
});

</script>
