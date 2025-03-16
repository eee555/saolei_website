<template>
    <el-row>
        <el-select v-model="option" size="small" style="width: 80px">
            <el-option v-for="(value, key) in options" :key="key" :label="value.label" :value="key">
            </el-option>
        </el-select>
        <span style="flex: 1" />
        <IconSetting>
            <Setting />
        </IconSetting>
    </el-row>
    <el-row :style="{ textAlign: 'center', height: `${BBBvSummaryConfig.cellHeight}px`, flexWrap: 'nowrap' }">
        <span style="width: 10%; min-width: 75px" />
        <span v-for="i in 10" style="width: 8.9%; min-width: 4em">{{ i - 1 }}</span>
    </el-row>
</template>

<script setup lang="ts">

import { ElRow, ElSelect, ElOption } from 'element-plus';
import IconSetting from '@/components/widgets/IconSetting.vue';
import Setting from './Setting.vue';
import { BBBvSummaryConfig } from '@/store';
import { ref, watch } from 'vue';
import { getStat_stat } from '@/utils/videoabstract';

type option_type = 'bvs' | 'time' | 'stnb' | 'ioe' | 'thrp';
const option = ref<option_type>(option_init())

interface Option {
    value: option_type;
    sortBy: getStat_stat;
    displayBy: getStat_stat;
    label: string;
    sortDesc: boolean;
}

const options = {
    'bvs': { value: 'bvs', sortBy: 'timems', displayBy: 'bvs', label: 'bvs', sortDesc: false },
    'time': { value: 'time', sortBy: 'timems', displayBy: 'time', label: 'time', sortDesc: false },
    'stnb': { value: 'stnb', sortBy: 'timems', displayBy: 'stnb', label: 'stnb', sortDesc: false },
    'ioe': { value: 'ioe', sortBy: 'ioe', displayBy: 'ioe', label: 'ioe', sortDesc: true },
    'thrp': { value: 'thrp', sortBy: 'thrp', displayBy: 'thrp', label: 'thrp', sortDesc: true },
} as Record<option_type, Option>;

watch(option, () => {
    BBBvSummaryConfig.value.displayBy = options[option.value].displayBy;
    BBBvSummaryConfig.value.sortBy = options[option.value].sortBy;
    BBBvSummaryConfig.value.sortDesc = options[option.value].sortDesc;
})

function option_init() {
    if (BBBvSummaryConfig.value.displayBy == 'bvs' && BBBvSummaryConfig.value.sortBy == 'timems') {
        return 'bvs';
    } else if (BBBvSummaryConfig.value.displayBy == 'time' && BBBvSummaryConfig.value.sortBy == 'timems') {
        return 'time';
    } else if (BBBvSummaryConfig.value.displayBy == 'stnb' && BBBvSummaryConfig.value.sortBy == 'timems') {
        return 'stnb';
    } else if (BBBvSummaryConfig.value.displayBy == 'ioe' && BBBvSummaryConfig.value.sortBy == 'ioe') {
        return 'ioe';
    } else if (BBBvSummaryConfig.value.displayBy == 'thrp' && BBBvSummaryConfig.value.sortBy == 'thrp') {
        return 'thrp';
    } else {
        return 'time';
    }
}

</script>