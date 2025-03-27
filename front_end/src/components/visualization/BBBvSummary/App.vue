<template>
    <Header v-if="header" />
    <el-row v-if="groupedVideoAbstract.size > 0" style="white-space: nowrap;">
        <YLabel :min-bv="minBv" :max-bv="maxBv" />
        <span
            :style="{ position: 'relative', width: '89%', minWidth: '40em', lineHeight: `${BBBvSummaryConfig.cellHeight}px` }"
        >
            <template v-for="bv in range(minBv, maxBv)" :key="bv">
                <Cell
                    :bv="bv" :level="level" :videos="groupedVideoAbstract.get(bv)" :color-theme="theme"
                    :display-by="options[BBBvSummaryConfig.template].displayBy"
                    :sort-by="options[BBBvSummaryConfig.template].sortBy"
                    :sort-desc="options[BBBvSummaryConfig.template].sortDesc" style="width: 10%" :software-filter="BBBvSummaryConfig.softwareFilter"
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
import { getStat_stat, groupVideosByBBBv } from '@/utils/videoabstract';
import { computed, PropType } from 'vue';
import Header from './Header.vue';
import Cell from './Cell.vue';
import YLabel from './YLabel.vue';
import { PiecewiseColorScheme } from '@/utils/colors';

const prop = defineProps({
    header: { type: Boolean, default: false },
    level: { type: String as PropType<MS_Level>, required: true },
})

type option_type = 'bvs' | 'time' | 'stnb' | 'ioe' | 'thrp' | 'custom';
interface Option {
    value: option_type;
    sortBy: getStat_stat;
    displayBy: getStat_stat;
    label: string;
    sortDesc: boolean;
}

const options = computed(() => {
    return {
        'bvs': { value: 'bvs', sortBy: 'timems', displayBy: 'bvs', label: 'bvs', sortDesc: false },
        'time': { value: 'time', sortBy: 'timems', displayBy: 'time', label: 'time', sortDesc: false },
        'stnb': { value: 'stnb', sortBy: 'timems', displayBy: 'stnb', label: 'stnb', sortDesc: false },
        'ioe': { value: 'ioe', sortBy: 'ioe', displayBy: 'ioe', label: 'ioe', sortDesc: true },
        'thrp': { value: 'thrp', sortBy: 'thrp', displayBy: 'thrp', label: 'thrp', sortDesc: true },
        'custom': { value: 'custom', sortBy: BBBvSummaryConfig.value.sortBy, displayBy: BBBvSummaryConfig.value.displayBy, label: 'custom', sortDesc: BBBvSummaryConfig.value.sortDesc },
    } as Record<option_type, Option>
});

const groupedVideoAbstract = computed(() => groupVideosByBBBv(store.player.videos, prop.level));
const maxBv = computed(() => setLastDigit(maximum(groupedVideoAbstract.value.keys()), 9));
const minBv = computed(() => setLastDigit(minimum(groupedVideoAbstract.value.keys()), 0));

const displayBy = computed(() => options.value[BBBvSummaryConfig.value.template].displayBy);

const theme = computed(() => {
    if (displayBy.value == 'bvs') {
        return new PiecewiseColorScheme(colorTheme.value.bvs.colors, colorTheme.value.bvs.thresholds);
    } else if (displayBy.value == 'stnb') {
        return new PiecewiseColorScheme(colorTheme.value.stnb.colors, colorTheme.value.stnb.thresholds);
    } else if (displayBy.value == 'ioe' || displayBy.value == 'thrp') {
        return new PiecewiseColorScheme(colorTheme.value.ioe.colors, colorTheme.value.ioe.thresholds);
    } else if (displayBy.value == 'time') {
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