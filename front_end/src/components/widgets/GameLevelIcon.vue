<template>
    <base-tooltip v-if="level == 'b'" :show-delay="500">
        <el-text v-t="'common.level.b'" />
        <template #content>
            <el-text>8x8/10</el-text>
        </template>
    </base-tooltip>
    <base-tooltip v-else-if="level == 'i'" :show-delay="500">
        <el-text v-t="'common.level.i'" />
        <template #content>
            <el-text>16x16/40</el-text>
        </template>
    </base-tooltip>
    <base-tooltip v-else-if="level == 'e'" :show-delay="500">
        <el-text v-t="'common.level.e'" />
        <template #content>
            <el-text>30x16/99</el-text>
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
    level: {
        type: String,
        default: "z",
    },
});
</script>