<template>
    <el-card style="overflow: auto">
        <div style="align-items: center; display: flex;">
            <el-text size="small">{{ t('msg.totalNVideos', [count]) }}</el-text>
            <span style="width: 10px;"></span>
        </div>
        <el-row>
            <el-text :style="{
                display:'inline-block',
                fontSize: (cellSize + cellMargin - 4) + 'px',
                marginTop: (cellSize + cellMargin) + 'px',
            }">
                Sun<br>Mon<br>Tue<br>Wed<br>Thu<br>Fri<br>Sat
            </el-text>
            <el-scrollbar style="flex:1;">
                <el-row>
                    <el-text v-for="date of generateMonthLabelRange(startDate, endDate)" :style="{
                        position: 'absolute',
                        top: 0,
                        left: (Math.max(1,(date.getTime()-startWeekTime) / fullWeek)) * (cellSize + cellMargin) + 'px',
                        transform: 'translate(-50%,0)'
                    }">{{ monthNameShort[date.getMonth()] }}</el-text>
                </el-row>
                <el-row style="position: relative; height: 139px;">
                    <template v-for="date of generateDateRange(startDate, endDate)">
                        <ActivityCalendarAbstractCell :date="date" :start-date="startDate"
                            :videos="groupedVideoAbstract.get(toISODateString(date))" :size="cellSize"
                            :corner-radius="5" :margin="cellMargin"
                            :x-offset="Math.round((getWeekTime(date) - startWeekTime) / fullWeek)" 
                            :y-offset="date.getDay()+1"/>
                    </template>
                </el-row>
            </el-scrollbar>
        </el-row>

    </el-card>
</template>

<script setup lang="ts">

import { computed, ref, watch } from 'vue';
import { store, local } from '@/store';
import { useDark, useElementSize } from '@vueuse/core';
import { useI18n } from 'vue-i18n';
import { groupVideosByUploadDate, VideoAbstract } from '@/utils/videoabstract';
import ActivityCalendarAbstractCell from './ActivityCalendarAbstractCell.vue';
import { fullWeek, getWeekTime, monthNameShort, toISODateString } from '@/utils/datetime';

const isDark = useDark();
const { t } = useI18n();

const count = ref(0);
const cellSize = ref(14);
const cellMargin = ref(3);

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

function generateMonthLabelRange(startDate: Date, endDate: Date) {
    let currentDate = new Date(startDate);
    if (currentDate.getDate() > 15) {
        currentDate.setMonth(currentDate.getMonth() + 1);
        currentDate.setDate(15);
    }
    let monthLabels = [];
    while (currentDate <= endDate) {
        monthLabels.push(currentDate);
        currentDate = new Date(currentDate);
        currentDate.setMonth(currentDate.getMonth() + 1);
    }
    return monthLabels;
}


const primaryColor = getComputedStyle(document.documentElement).getPropertyValue('--el-color-primary');

</script>

<style scoped lang="less">
.el-card {
    --el-card-padding: 10px;
}
</style>