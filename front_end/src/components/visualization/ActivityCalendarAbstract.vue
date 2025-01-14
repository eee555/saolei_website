<template>
    <el-card style="overflow: auto">
        <div style="align-items: center; display: flex;">
            <el-text size="small">{{ t('msg.totalNVideos', [count]) }}</el-text>
            <span style="width: 10px;"></span>
        </div>
        <el-row>
            <div style="display:inline-block;font-size: 13px;margin-top: 17px;">
                Sun<br>Mon<br>Tue<br>Wed<br>Thu<br>Fri<br>Sat
            </div>
            <el-scrollbar style="flex:1;">
                <div style="position: relative; height: 139px;">
                    <template v-for="date of generateDateRange(startDate, endDate)">
                        <el-text v-if="date.getDate() === 15" :style="{
                            position: 'absolute',
                            top: 0,
                            left: (Math.max(1,(date.getTime()-startWeekTime) / fullWeek)) * 17 + 'px',
                            transform: 'translate(-50%,0)'
                        }">{{ monthNameShort[date.getMonth()] }}</el-text>
                        <ActivityCalendarAbstractCell :date="date" :start-date="startDate"
                            :videos="groupedVideoAbstract.get(date.toISOString().split('T')[0])" :size="14"
                            :corner-radius="5" :margin="3"
                            :x-offset="Math.round((getWeekTime(date) - startWeekTime) / fullWeek)" 
                            :y-offset="date.getDay()+1"/>
                    </template>

                    <!-- {{ date.toISOString().split('T')[0] }} -->
                </div>
            </el-scrollbar>
        </el-row>

    </el-card>
</template>

<script setup lang="ts">

import { computed, ref, watch } from 'vue';
import { store, local } from '@/store';
import { useDark, useElementSize } from '@vueuse/core';
import { useI18n } from 'vue-i18n';
import MSLevelFilter from '../Filters/MSLevelFilter.vue';
import { groupVideosByUploadDate, VideoAbstract } from '@/utils/videoabstract';
import { MS_Levels } from '@/utils/ms_const';
import ActivityCalendarAbstractCell from './ActivityCalendarAbstractCell.vue';
import { fullWeek, getWeekTime, monthNameShort } from '@/utils/datetime';

const isDark = useDark();
const { t } = useI18n();

const count = ref(0);
const cellSize = ref(14);

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



const primaryColor = getComputedStyle(document.documentElement).getPropertyValue('--el-color-primary');

</script>

<style scoped lang="less">
.el-card {
    --el-card-padding: 10px;
}
</style>