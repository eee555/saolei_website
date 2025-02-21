<template>
    <el-row :style="{textAlign: 'center', height: BBBvSummaryConfig.cellHeight + 'px'}">
        <IconSetting style="width: 10%; min-width: 75px"><Setting/></IconSetting>
        <span v-for="i in 10" style="flex: 1; min-width: 3em">{{ i-1 }}</span>
    </el-row>
</template>

<script setup lang="ts">

import { ElRow } from 'element-plus';
import IconSetting from '@/components/widgets/IconSetting.vue';
import Setting from './Setting.vue';
import { BBBvSummaryConfig } from '@/store';

const prop = defineProps({

})

</script>