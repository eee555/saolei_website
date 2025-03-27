<template>
    <base-tooltip v-if="software == 'a'" :show-delay="500">
        <img style="width: 16px; height: 16px" src="../../assets/img/ms_arbiter_MAINICON.ico">
        <template #content>
            <el-text>Minesweeper Arbiter</el-text>
        </template>
    </base-tooltip>
    <base-tooltip v-else-if="software == 'e'" :show-delay="500">
        <img style="width: 16px; height: 16px" src="../../assets/img/img_meta.png">
        <template #content>
            <el-text v-t="'common.software.metasweeper'" />
        </template>
    </base-tooltip>
    <base-tooltip v-else-if="software == 'm'" :show-delay="500">
        <img style="width: 16px; height: 16px" src="../../assets/img/clone2007.ico">
        <template #content>
            <el-text>Clone 2007</el-text>
        </template>
    </base-tooltip>
    <base-tooltip v-else-if="software == 'r'" :show-delay="500">
        <img style="width: 16px; height: 16px" src="../../assets/img/viennasweeper.ico">
        <template #content>
            <el-text>Viennasweeper</el-text>
        </template>
    </base-tooltip>
    <el-text v-else type="danger">
        <QuestionFilled style="width: 16px; height: 16px" />
    </el-text>
</template>

<script setup lang="ts">
import { ElText } from 'element-plus';
import BaseTooltip from '@/components/common/BaseTooltip.vue';

defineProps({
    software: {
        type: String,
        default: "z",
    },
});
</script>
