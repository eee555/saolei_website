<template>
    <el-text v-t="'activityCalendar.showDate'"/>&nbsp;
    <el-switch v-model="activityCalendarConfig.showDate" size="small"/><br>
    <el-text v-t="'activityCalendar.cellSize'"/>&nbsp;
    <el-input-number v-model="activityCalendarConfig.cellSize" :min="1" :max="20" size="small" controls-position="right"/><br>
    <el-text v-t="'activityCalendar.cellGap'"/>&nbsp;
    <el-input-number v-model="activityCalendarConfig.cellMargin" :min="0" :max="10" size="small" controls-position="right" /><br>
    <el-text v-t="'activityCalendar.cornerRadius'"/>&nbsp;
    <el-input-number v-model="activityCalendarConfig.cornerRadius" :min="0" :max="50" size="small" controls-position="right" >
        <template #suffix>
            %
        </template>
    </el-input-number>
</template>

<script setup lang="ts">
import { activityCalendarConfig } from '@/store';
import { ElSwitch, ElInputNumber, ElText } from 'element-plus';

</script>

<style lang="less" scoped>

.el-input-number--small {
    width: 75px;
}

</style>