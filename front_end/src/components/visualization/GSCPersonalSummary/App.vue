<template>
    <div class="layout-row">
        <AllSums :sum-time="bStat.time + iStat.time + eStat.time" :sum-bvs="bStat.bvs + iStat.bvs + eStat.bvs" :sum-stnb="bStat.stnb + iStat.stnb + eStat.stnb" />
    </div>
    <div style="height: 20px" />
    <div class="layout-row">
        <span style="flex: 1" />
        <div class="summary-level">
            <LevelBlock ref="BBlockRef" level="b" :videos="videos" />
        </div>
        <span style="flex: 1" />
        <div class="summary-level">
            <LevelBlock ref="IBlockRef" level="i" :videos="videos" />
            <div style="height: 25px" />
            <LevelBlock ref="EBlockRef" level="e" :videos="videos" />
        </div>
        <span style="flex: 1" />
    </div>
    <div style="height: 20px" />
    <div class="layout-row">
        <AllSums :sum-time="bStat.time + iStat.time + eStat.time" :sum-bvs="bStat.bvs + iStat.bvs + eStat.bvs" :sum-stnb="bStat.stnb + iStat.stnb + eStat.stnb" />
    </div>
</template>

<script setup lang="ts">
import '@/styles/layout.css';
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

<style scoped>
.summary-level {
    box-sizing: border-box;
    flex: 0 0 calc(100% * 10 / 24);
    min-width: 16em;
}
</style>
