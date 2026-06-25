<template>
    <ElRow>
        <AllSums :sum-time="bStat.time + iStat.time + eStat.time" :sum-bvs="bStat.bvs + iStat.bvs + eStat.bvs" :sum-stnb="bStat.stnb + iStat.stnb + eStat.stnb" />
    </ElRow>
    <ElRow style="height: 20px" />
    <ElRow>
        <span style="flex: 1" />
        <ElCol :span="10" style="min-width: 16em">
            <LevelBlock ref="BBlockRef" level="b" :videos="videos" />
        </ElCol>
        <span style="flex: 1" />
        <ElCol :span="10" style="min-width: 16em">
            <LevelBlock ref="IBlockRef" level="i" :videos="videos" />
            <ElRow style="height: 25px" />
            <LevelBlock ref="EBlockRef" level="e" :videos="videos" />
        </ElCol>
        <span style="flex: 1" />
    </ElRow>
    <ElRow style="height: 20px" />
    <ElRow>
        <AllSums :sum-time="bStat.time + iStat.time + eStat.time" :sum-bvs="bStat.bvs + iStat.bvs + eStat.bvs" :sum-stnb="bStat.stnb + iStat.stnb + eStat.stnb" />
    </ElRow>
</template>

<script setup lang="ts">
import { ElCol, ElRow } from 'element-plus';
import type { PropType } from 'vue';
import { computed, useTemplateRef } from 'vue';

import AllSums from './AllSums.vue';
import LevelBlock from './LevelBlock.vue';

import type { VideoAbstract } from '@/utils/videoabstract';

defineProps({
    videos: {
        type: Array as PropType<VideoAbstract[]>,
        default: () => [],
    },
});

type LevelBlockInstance = InstanceType<typeof LevelBlock>;

const BBlockRef = useTemplateRef<LevelBlockInstance>('BBlockRef');
const IBlockRef = useTemplateRef<LevelBlockInstance>('IBlockRef');
const EBlockRef = useTemplateRef<LevelBlockInstance>('EBlockRef');

const bStat = computed(() => {
    return BBlockRef.value === null
        ? { time: 0, bvs: 0, stnb: 0 }
        : BBlockRef.value.sumAll;
});

const iStat = computed(() => {
    return IBlockRef.value === null
        ? { time: 0, bvs: 0, stnb: 0 }
        : IBlockRef.value.sumAll;
});

const eStat = computed(() => {
    return EBlockRef.value === null
        ? { time: 0, bvs: 0, stnb: 0 }
        : EBlockRef.value.sumAll;
});
</script>
