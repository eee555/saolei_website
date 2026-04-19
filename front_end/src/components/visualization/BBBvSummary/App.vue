<template>
    <el-row v-if="header" :style="{ textAlign: 'center', height: '25px', flexWrap: 'nowrap', marginTop: '10px', marginBottom: '-20px' }">
        <span style="width: 10%; min-width: 75px" />
        <span :style="gridStyle">
            <span v-for="i in 10" :key="i" class="text text-small">
                {{ i - 1 }}
            </span>
        </span>
    </el-row>
    <el-divider data-cy="summary" style="margin: 18px 0 12px 0;">
        <span class="text">
            {{ t(`common.level.${level}`) }}
            &nbsp;
            {{ t('BBBvSummary.bbbvInTotal', [groupedVideoAbstract.size]) }}
        </span>
    </el-divider>
    <el-row v-if="groupedVideoAbstract.size > 0" style="white-space: nowrap;">
        <YLabel :min-bv="minBv" :max-bv="maxBv" />
        <tippy :duration="0" sticky follow-cursor :style="gridStyle">
            <Cell
                v-for="bv in ArrayUtils.range(minBv, maxBv)"
                :key="bv"
                :data-cy="`bv-${bv}`"
                :bv="bv"
                :level="level"
                :videos="groupedVideoAbstract.get(bv)"
                :color-theme="theme"
                :display-by="options[BBBvSummaryConfig.template].displayBy"
                :sort-by="options[BBBvSummaryConfig.template].sortBy"
                :sort-desc="options[BBBvSummaryConfig.template].sortDesc"
                :software-filter="BBBvSummaryConfig.softwareFilter"
                :tooltip-mode="BBBvSummaryConfig.tooltipMode"
                :show-icon="BBBvSummaryConfig.showIcon"
                @mouseover="tooltipVideos=groupedVideoAbstract.get(bv) || []"
            />
            <template #content>
                <Tooltip
                    :videos="tooltipVideos"
                    :sort-by="options[BBBvSummaryConfig.template].sortBy"
                    :sort-desc="options[BBBvSummaryConfig.template].sortDesc"
                    :software-filter="BBBvSummaryConfig.softwareFilter"
                />
            </template>
        </tippy>
    </el-row>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import { ElDivider, ElRow } from 'element-plus';
import { computed, PropType, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { Tippy } from 'vue-tippy';

import Cell from './Cell.vue';
import Tooltip from './Tooltip.vue';
import YLabel from './YLabel.vue';

import { BBBvSummaryConfig, colorTheme } from '@/store';
import { ArrayUtils } from '@/utils/arrays';
import { PiecewiseColorScheme } from '@/utils/colors';
import { setLastDigit } from '@/utils/math';
import { CellChoice, ColorTemplateName, MS_Level } from '@/utils/ms_const';
import { getStat_stat, groupVideosByBBBv, VideoAbstract } from '@/utils/videoabstract';

const { t } = useI18n();
const tooltipVideos = ref([] as VideoAbstract[]);

const prop = defineProps({
    header: { type: Boolean, default: false },
    level: { type: String as PropType<MS_Level>, required: true },
    videoList: { type: Array<VideoAbstract>, default: () => [] },
});

interface Option {
    value: ColorTemplateName;
    sortBy: getStat_stat;
    displayBy: CellChoice;
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
        'ces': { value: 'ces', sortBy: 'ces', displayBy: 'ces', label: 'ces', sortDesc: true },
        'cls': { value: 'cls', sortBy: 'cls', displayBy: 'cls', label: 'cls', sortDesc: true },
        'custom': { value: 'custom', sortBy: BBBvSummaryConfig.value.sortBy, displayBy: BBBvSummaryConfig.value.displayBy, label: 'custom', sortDesc: BBBvSummaryConfig.value.sortDesc },
    } as Record<ColorTemplateName, Option>;
});

const groupedVideoAbstract = computed(() => groupVideosByBBBv(prop.videoList, prop.level));
const maxBv = computed(() => setLastDigit(ArrayUtils.maximum(groupedVideoAbstract.value.keys()), 9));
const minBv = computed(() => setLastDigit(ArrayUtils.minimum(groupedVideoAbstract.value.keys()), 0));

const displayBy = computed(() => options.value[BBBvSummaryConfig.value.template].displayBy);

const theme = computed(() => {
    if (['bvs', 'cls', 'ces'].includes(displayBy.value)) {
        return new PiecewiseColorScheme(colorTheme.value.bvs.colors, colorTheme.value.bvs.thresholds);
    } else if (displayBy.value == 'stnb') {
        return new PiecewiseColorScheme(colorTheme.value.stnb.colors, colorTheme.value.stnb.thresholds);
    } else if (['ioe', 'thrp', 'iome'].includes(displayBy.value)) {
        return new PiecewiseColorScheme(colorTheme.value.ioe.colors, colorTheme.value.ioe.thresholds);
    } else if (displayBy.value == 'time') {
        if (prop.level == 'b') return new PiecewiseColorScheme(colorTheme.value.btime.colors, colorTheme.value.btime.thresholds);
        else if (prop.level == 'i') return new PiecewiseColorScheme(colorTheme.value.itime.colors, colorTheme.value.itime.thresholds);
        else if (prop.level == 'e') return new PiecewiseColorScheme(colorTheme.value.etime.colors, colorTheme.value.etime.thresholds);
        else return new PiecewiseColorScheme([], []);
    } else return new PiecewiseColorScheme([], []);
});

const gridStyle = computed(() => {
    return {
        'display': 'grid',
        width: '89%',
        minWidth: BBBvSummaryConfig.value.showIcon === '' ? '45em' : '54em',
        gridTemplateColumns: 'repeat(10, 1fr)',
        gridAutoRows: '25px',
    };
});

</script>

<style lang="less" scoped>
.el-row {
    flex-wrap: nowrap;
}
</style>
