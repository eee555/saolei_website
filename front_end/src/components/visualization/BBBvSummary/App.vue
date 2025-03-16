<template>
    <Header v-if="header" />
    <el-row v-if="groupedVideoAbstract.size > 0" style="white-space: nowrap;">
        <YLabel :min-bv="minBv" :max-bv="maxBv" />
        <span
            :style="{ position: 'relative', width: '89%', minWidth: '40em', lineHeight: `${BBBvSummaryConfig.cellHeight}px` }"
        >
            <template v-for="bv in range(minBv, maxBv)" :key="bv">
                <Cell 
                    :bv="bv" :level="level" :videos="groupedVideoAbstract.get(bv)" :x-offset="getLastDigit(bv)"
                    :y-offset="Math.floor((bv - minBv) / 10)" :color-theme="theme" :display-by="BBBvSummaryConfig.displayBy" :sort-by="BBBvSummaryConfig.sortBy" :sort-desc="BBBvSummaryConfig.sortDesc" style="width: 10%"
                />
                <br v-if="getLastDigit(bv) == 9">
            </template>
        </span>
    </el-row>
</template>

<script setup lang="ts">
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
    if (BBBvSummaryConfig.value.displayBy == 'bvs') {
        return new PiecewiseColorScheme(colorTheme.value.bvs.colors, colorTheme.value.bvs.thresholds);
    } else if (BBBvSummaryConfig.value.displayBy == 'stnb') {
        return new PiecewiseColorScheme(colorTheme.value.stnb.colors, colorTheme.value.stnb.thresholds);
    } else if (BBBvSummaryConfig.value.displayBy == 'ioe' || BBBvSummaryConfig.value.displayBy == 'thrp') {
        return new PiecewiseColorScheme(colorTheme.value.ioe.colors, colorTheme.value.ioe.thresholds);
    } else if (BBBvSummaryConfig.value.displayBy == 'time') {
        if (prop.level == 'b') return new PiecewiseColorScheme(colorTheme.value.btime.colors, colorTheme.value.btime.thresholds);
        else if (prop.level == 'i') return new PiecewiseColorScheme(colorTheme.value.itime.colors, colorTheme.value.itime.thresholds);
        else if (prop.level == 'e') return new PiecewiseColorScheme(colorTheme.value.etime.colors, colorTheme.value.etime.thresholds);
        else return new PiecewiseColorScheme([], []);
    }
    else return new PiecewiseColorScheme([], []);
})

</script>

<style lang="less" scoped>
.el-row {
    flex-wrap: nowrap;
}
</style>