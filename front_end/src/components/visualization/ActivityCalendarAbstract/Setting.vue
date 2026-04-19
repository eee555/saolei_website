<template>
    <span class="text">{{ t('local.showDate') }}</span>&nbsp;
    <el-switch v-model="activityCalendarConfig.showDate" size="small" /><br>
    <span class="text">{{ t('local.useEndTime') }}</span>&nbsp;
    <el-switch v-model="activityCalendarConfig.useEndTime" size="small" />&nbsp;
    <base-tooltip>
        <base-icon-question />
        <template #content>
            {{ t('local.useEndTimeTooltip') }}
        </template>
    </base-tooltip><br>
    <span class="text">{{ t('local.cellSize') }}</span>&nbsp;
    <el-input-number v-model="activityCalendarConfig.cellSize" :min="1" :max="20" size="small" controls-position="right" /><br>
    <span class="text">{{ t('local.cellGap') }}</span>&nbsp;
    <el-input-number v-model="activityCalendarConfig.cellMargin" :min="0" :max="10" size="small" controls-position="right" /><br>
    <span class="text">{{ t('local.cornerRadius') }}</span>&nbsp;
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

/* 本地化 Localization */
const i18nMessages = {
    'zh-cn': { local: {
        cellGap: '方格间距',
        cellSize: '方格边长',
        cornerRadius: '圆角半径',
        showDate: '显示日期',
        useEndTime: '结束时间',
        useEndTimeTooltip: '依录像结束时间显示，关闭此项将使用录像上传时间。结束时间为用户的系统时间，可能不准确。',
    } },
    'en': { local: {
        cellGap: 'Cell Gap',
        cellSize: 'Cell Size',
        cornerRadius: 'Corner Radius',
        showDate: 'Show Date',
        useEndTime: 'Display by finishing time',
        useEndTimeTooltip: 'Display by the time of finishing games when switching on, and the time of uploading when switching off. The finishing time represents the user\'s system time and can be incorrect.',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>

<style lang="less" scoped>

.el-input-number--small {
    width: 75px;
}

</style>
