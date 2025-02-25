<template>
    <el-row>
        <el-select v-model="option" size="small" style="width: 80px">
            <el-option v-for="(value, key) in options" :key="key" :label="value.label" :value="key">
            </el-option>
        </el-select>
        <span style="flex: 1"/>
        <IconSetting>
            <Setting />
        </IconSetting>
    </el-row>
    <el-row :style="{ textAlign: 'center', height: BBBvSummaryConfig.cellHeight + 'px', flexWrap: 'nowrap' }">
        <span style="width: 10%; min-width: 75px"/>
        <span v-for="i in 10" style="width: 8.9%; min-width: 4em">{{ i - 1 }}</span>
    </el-row>
</template>

<script setup lang="ts">

import { ElRow, ElSelect, ElOption } from 'element-plus';
import IconSetting from '@/components/widgets/IconSetting.vue';
import Setting from './Setting.vue';
import { BBBvSummaryConfig } from '@/store';
import { ref, watch } from 'vue';

type option_type = 'bvs' | 'time' | 'stnb';
const option = ref<option_type>(option_init())

const options = {
    'bvs': { value: 'bvs', sortBy: 'timems', displayBy: 'bvs', label: 'bvs' },
    'time': { value: 'time', sortBy: 'timems', displayBy: 'time', label: 'time' },
    'stnb': { value: 'stnb', sortBy: 'timems', displayBy: 'stnb', label: 'stnb' },
};

watch(option, () => {
    BBBvSummaryConfig.value.displayBy = options[option.value].displayBy;
    BBBvSummaryConfig.value.sortBy = options[option.value].sortBy;
})

function option_init() {
    if (BBBvSummaryConfig.value.displayBy == 'bvs' && BBBvSummaryConfig.value.sortBy == 'timems') {
        return 'bvs';
    } else if (BBBvSummaryConfig.value.displayBy == 'time' && BBBvSummaryConfig.value.sortBy == 'timems') {
        return 'time';
    } else if (BBBvSummaryConfig.value.displayBy == 'stnb' && BBBvSummaryConfig.value.sortBy == 'timems') {
        return 'stnb';
    } else {
        return 'time';
    }
}

</script>