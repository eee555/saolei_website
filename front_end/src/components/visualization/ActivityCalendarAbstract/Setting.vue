<template>
    <el-text>{{ t('activityCalendar.showDate') }}</el-text>&nbsp;
    <el-switch v-model="activityCalendarConfig.showDate" size="small" /><br>
    <el-text>{{ t('activityCalendar.useEndTime') }}</el-text>&nbsp;
    <el-switch v-model="activityCalendarConfig.useEndTime" size="small" />&nbsp;
    <base-tooltip>
        <base-icon-question />
        <template #content>
            {{ t('activityCalendar.useEndTimeTooltip') }}
        </template>
    </base-tooltip><br>
    <el-text>{{ t('activityCalendar.cellSize') }}</el-text>&nbsp;
    <el-input-number v-model="activityCalendarConfig.cellSize" :min="1" :max="20" size="small" controls-position="right" /><br>
    <el-text>{{ t('activityCalendar.cellGap') }}</el-text>&nbsp;
    <el-input-number v-model="activityCalendarConfig.cellMargin" :min="0" :max="10" size="small" controls-position="right" /><br>
    <el-text>{{ t('activityCalendar.cornerRadius') }}</el-text>&nbsp;
    <el-input-number v-model="activityCalendarConfig.cornerRadius" :min="0" :max="50" size="small" controls-position="right">
        <template #suffix>
            %
        </template>
    </el-input-number>
</template>

<script setup lang="ts">
import { activityCalendarConfig } from '@/store';
import { ElSwitch, ElInputNumber, ElText } from 'element-plus';
import { useI18n } from 'vue-i18n';
import BaseIconQuestion from '@/components/common/BaseIconQuestion.vue';
import BaseTooltip from '@/components/common/BaseTooltip.vue';

const { t } = useI18n();

</script>

<style lang="less" scoped>

.el-input-number--small {
    width: 75px;
}

</style>
