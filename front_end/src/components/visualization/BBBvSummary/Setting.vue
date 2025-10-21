<template>
    <el-text>{{ t('BBBvSummary.cellHeight') }}</el-text>
    &nbsp;
    <el-input-number v-model="BBBvSummaryConfig.cellHeight" :min="10" :max="30" size="small" controls-position="right" style="width: 60px;" />
</template>

<script setup lang="ts">
import { ElInputNumber, ElText } from 'element-plus';
import { useI18n } from 'vue-i18n';

import { BBBvSummaryConfig } from '@/store';

const { t } = useI18n();
</script>
