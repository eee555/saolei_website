<template>
    <el-text>行高</el-text>
    <el-input-number v-model="BBBvSummaryConfig.cellHeight" :min="10" :max="30" size="small" controls-position="right" />
</template>

<script setup lang="ts">
import { BBBvSummaryConfig } from '@/store';
import { ElText, ElInputNumber } from 'element-plus';

</script>