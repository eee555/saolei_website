<template>
        <Header v-if="header" />
        <el-row>
            <YLabel :minBv="minBv" :maxBv="maxBv" />
            <span :style="{ position: 'relative', height: (maxBv - minBv + 1) / 10 * BBBvSummaryConfig.cellHeight + 'px', flex: '1' }">
                <Cell v-for="bv in range(minBv, maxBv)" :bv="bv" :level="level" :videos="groupedVideoAbstract.get(bv)"
                    :x-offset="getLastDigit(bv)" :y-offset="Math.floor((bv - minBv) / 10)" :color-theme="theme" />
            </span>
        </el-row>
</template>

<script setup lang="ts">

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import { BBBvSummaryConfig, colorTheme, store } from '@/store';
import { ElRow } from 'element-plus';
import { maximum, minimum, range } from '@/utils/arrays';
import { getLastDigit, setLastDigit } from '@/utils/math';
import { MS_Level } from '@/utils/ms_const';
import { groupVideosByBBBv } from '@/utils/videoabstract';
import { computed, PropType } from 'vue';
import Header from './Header.vue';
import Cell from './Cell.vue';
import YLabel from './YLabel.vue';
import { PiecewiseColorScheme } from '@/utils/colors';

const prop = defineProps({
    header: { type: Boolean, default: false },
    level: { type: String as PropType<MS_Level>, required: true },
})

const groupedVideoAbstract = computed(() => groupVideosByBBBv(store.player.videos, prop.level));
const maxBv = computed(() => setLastDigit(maximum(groupedVideoAbstract.value.keys()), 9));
const minBv = computed(() => setLastDigit(minimum(groupedVideoAbstract.value.keys()), 0));

const theme = computed(() => {
    if (prop.level == 'b') return new PiecewiseColorScheme(colorTheme.value.btime.colors, colorTheme.value.btime.thresholds);
    else if (prop.level == 'i') return new PiecewiseColorScheme(colorTheme.value.itime.colors, colorTheme.value.itime.thresholds);
    else if (prop.level == 'e') return new PiecewiseColorScheme(colorTheme.value.etime.colors, colorTheme.value.etime.thresholds);
    else return new PiecewiseColorScheme([], []);
})

</script>