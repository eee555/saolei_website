<template>
    <el-card style="overflow: auto;">
        <el-row style="align-items: center; display: flex;">
            <Header />
        </el-row>
        <el-row>
            <DayLabel />
            <el-scrollbar style="flex:1;">
                <el-row>
                    <MonthLabel :start-date="startDate" :end-date="endDate" />
                </el-row>
                <el-row :style="{
                    position: 'relative',
                    height: (cellFullSize * 8 + activityCalendarConfig.cellMargin) + 'px',
                    filter: 'invert(' + (local.darkmode ? 0 : 1) + ')',
                }">
                    <template v-for="date of generateDateRange(startDate, endDate)">
                        <Cell :date="date" :start-date="startDate"
                            :videos="groupedVideoAbstract.get(toISODateString(date))"
                            :x-offset="Math.round((getWeekTime(date) - startWeekTime) / fullWeek)"
                            :y-offset="date.getDay() + 1" :show-date="activityCalendarConfig.showDate" />
                    </template>
                </el-row>
            </el-scrollbar>
        </el-row>
    </el-card>
</template>

<script setup lang="ts">

import { computed, defineAsyncComponent } from 'vue';
import { store, activityCalendarConfig, local } from '@/store';
import { groupVideosByUploadDate } from '@/utils/videoabstract';
import { fullWeek, getWeekTime, toISODateString } from '@/utils/datetime';
import { ElCard, ElRow, ElScrollbar } from 'element-plus';
import Header from './Header.vue';
import DayLabel from './DayLabel.vue';
import MonthLabel from './MonthLabel.vue';
const Cell = defineAsyncComponent(() => import('./Cell.vue'));

const cellFullSize = computed(() => activityCalendarConfig.value.cellSize + activityCalendarConfig.value.cellMargin);

const groupedVideoAbstract = computed(() => groupVideosByUploadDate(store.player.videos));
const endDate = new Date(new Date().toDateString()); // today
const startDate = computed(() => {
    const keys = groupedVideoAbstract.value.keys();
    let min = new Date(endDate);
    min.setFullYear(min.getFullYear() - 1);
    min.setDate(min.getDate() + 1);
    for (const key of keys) {
        let keydate = new Date(key);
        if (keydate < min) min = keydate;
    }
    return min;
})
const startWeekTime = computed(() => getWeekTime(startDate.value));

function* generateDateRange(startDate: Date, endDate: Date, step: number = 1) {
    let currentDate = new Date(startDate);
    while (currentDate <= endDate) {
        yield new Date(currentDate);  // Yield a new Date object (to avoid modifying the original one)
        currentDate.setDate(currentDate.getDate() + step); // Increment by 1 day (or custom step)
    }
}

</script>

<style scoped lang="less">
.el-card {
    --el-card-padding: 10px;
}
</style>