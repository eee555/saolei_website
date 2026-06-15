<template>
    <ElRow v-if="header" :style="{ textAlign: 'center', height: '25px', flexWrap: 'nowrap', marginTop: '10px', marginBottom: '-20px' }">
        <span style="width: 10%; min-width: 4em" />
        <span :style="gridStyle">
            <span v-for="i in 10" :key="i" class="text text-small">
                {{ i - 1 }}
            </span>
        </span>
    </ElRow>
    <ElDivider data-cy="summary" style="margin: 18px 0 12px 0;">
        <span class="text">
            {{ t(`common.level.${level}`) }}
            &nbsp;
            {{ t('BBBvSummary.bbbvInTotal', [groupedVideoAbstract.size]) }}
        </span>
    </ElDivider>
    <ElRow v-if="groupedVideoAbstract.size > 0" style="white-space: nowrap;">
        <YLabel :min-bv="minBv" :max-bv="maxBv" />
        <Tippy :duration="0" sticky follow-cursor :style="gridStyle">
            <Cell
                v-for="bv in ArrayUtils.range(minBv, maxBv)"
                :key="bv"
                :data-cy="`bv-${bv}`"
                :videos="groupedVideoAbstract.get(bv)"
                :color-theme="theme"
                :display-by="options[BBBvSummaryConfig.template].displayBy"
                :sort-by="options[BBBvSummaryConfig.template].sortBy"
                :sort-desc="options[BBBvSummaryConfig.template].sortDesc"
                :software-filter="BBBvSummaryConfig.softwareFilter"
                :tooltip-mode="BBBvSummaryConfig.tooltipMode"
                :show-icon="BBBvSummaryConfig.showIcon"
                :new-thresh="BBBvSummaryConfig.newThresh"
                :new-date-field="BBBvSummaryConfig.newDateField"
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
        </Tippy>
    </ElRow>
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
import { CellChoice, ColorTemplateName, getPiecewiseColorSchemeName, MS_Level, PiecewiseColorSchemeName } from '@/utils/ms_const';
import { getStat_stat, groupVideosByBBBv, VideoAbstract } from '@/utils/videoabstract';

const prop = defineProps({
    header: { type: Boolean, default: false },
    level: { type: String as PropType<MS_Level>, required: true },
    videoList: { type: Array<VideoAbstract>, default: () => [] },
});
const { t } = useI18n();
const tooltipVideos = ref([] as VideoAbstract[]);

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
    if (!(PiecewiseColorSchemeName as readonly string[]).includes(displayBy.value)) return new PiecewiseColorScheme([], []);
    const themeName = getPiecewiseColorSchemeName(displayBy.value as PiecewiseColorSchemeName, prop.level);
    return new PiecewiseColorScheme(colorTheme.value[themeName].colors, colorTheme.value[themeName].thresholds);
});

const gridStyle = computed(() => {
    return {
        'display': 'grid',
        width: '89%',
        minWidth: BBBvSummaryConfig.value.showIcon === '' ? '37em' : '48em',
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
