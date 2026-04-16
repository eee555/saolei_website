<template>
    <span class="text">{{ t('activityCalendar.showDate') }}</span>&nbsp;
    <el-switch v-model="activityCalendarConfig.showDate" size="small" /><br>
    <span class="text">{{ t('activityCalendar.useEndTime') }}</span>&nbsp;
    <el-switch v-model="activityCalendarConfig.useEndTime" size="small" />&nbsp;
    <base-tooltip>
        <base-icon-question />
        <template #content>
            {{ t('activityCalendar.useEndTimeTooltip') }}
        </template>
    </base-tooltip><br>
    <span class="text">{{ t('activityCalendar.cellSize') }}</span>&nbsp;
    <el-input-number v-model="activityCalendarConfig.cellSize" :min="1" :max="20" size="small" controls-position="right" /><br>
    <span class="text">{{ t('activityCalendar.cellGap') }}</span>&nbsp;
    <el-input-number v-model="activityCalendarConfig.cellMargin" :min="0" :max="10" size="small" controls-position="right" /><br>
    <span class="text">{{ t('activityCalendar.cornerRadius') }}</span>&nbsp;
    <el-input-number v-model="activityCalendarConfig.cornerRadius" :min="0" :max="50" size="small" controls-position="right">
        <template #suffix>
            %
        </template>
    </el-input-number>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import { ElInputNumber, ElSwitch } from 'element-plus';
import { useI18n } from 'vue-i18n';

import BaseTooltip from '@/components/common/BaseTooltip.vue';
import { BaseIconQuestion } from '@/components/common/icon';
import { activityCalendarConfig } from '@/store';

const { t } = useI18n();

</script>

<style lang="less" scoped>

.el-input-number--small {
    width: 75px;
}

</style>
