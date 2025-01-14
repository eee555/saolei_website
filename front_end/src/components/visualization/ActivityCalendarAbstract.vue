<template>
    <el-card style="overflow: auto">
        <el-row style="align-items: center; display: flex;">
            <el-text size="small">{{ t('activityCalendar.totalNVideos', [store.player.videos.length]) }}</el-text>
            <span style="flex: 1;"></span>
            <span class="dot" style=" background-color: #c00;" />
            <el-text size="small">{{ t('common.level.shortb') }}</el-text>
            &nbsp;
            <span class="dot" style=" background-color: #0c0;" />
            <el-text size="small">{{ t('common.level.shorti') }}</el-text>
            &nbsp;
            <span class="dot" style=" background-color: #00c;" />
            <el-text size="small">{{ t('common.level.shorte') }}</el-text>
            <span style="width: 10px;"></span>
            <IconSetting>
                <ActivityCalendarAbstractSetting />
            </IconSetting>
        </el-row>
        <el-row>
            <el-text :style="{
                display: 'inline-block',
                fontSize: (cellFullSize - 8) + 'px',
                lineHeight: cellFullSize + 'px',
                marginTop: cellFullSize + 'px',
                marginRight: activityCalendarConfig.cellMargin + 'px',
            }">
                Sun<br>Mon<br>Tue<br>Wed<br>Thu<br>Fri<br>Sat
            </el-text>
            <el-scrollbar style="flex:1;">
                <el-row>
                    <el-text v-for="date of generateMonthLabelRange(startDate, endDate)" :style="{
                        position: 'absolute',
                        fontSize: '12px',
                        top: 0,
                        left: (Math.max(1, (date.getTime() - startWeekTime) / fullWeek)) * cellFullSize + 'px',
                        transform: 'translate(-50%,0)'
                    }">{{ monthNameShort[date.getMonth()] }}</el-text>
                </el-row>
                <el-row :style="{
                    position: 'relative',
                    height: (cellFullSize*8+activityCalendarConfig.cellMargin)+'px',
                }">
                    <template v-for="date of generateDateRange(startDate, endDate)">
                        <ActivityCalendarAbstractCell :date="date" :start-date="startDate"
                            :videos="groupedVideoAbstract.get(toISODateString(date))" :size="activityCalendarConfig.cellSize"
                            :corner-radius="activityCalendarConfig.cornerRadius" :margin="activityCalendarConfig.cellMargin"
                            :x-offset="Math.round((getWeekTime(date) - startWeekTime) / fullWeek)"
                            :y-offset="date.getDay() + 1" :show-date="activityCalendarConfig.showDate" />
                    </template>
                </el-row>
            </el-scrollbar>
        </el-row>

    </el-card>
</template>

<script setup lang="ts">

import { computed } from 'vue';
import { store, activityCalendarConfig } from '@/store';
import { useI18n } from 'vue-i18n';
import { groupVideosByUploadDate } from '@/utils/videoabstract';
import ActivityCalendarAbstractCell from './ActivityCalendarAbstractCell.vue';
import { fullWeek, getWeekTime, monthNameShort, toISODateString } from '@/utils/datetime';
import IconSetting from '../widgets/IconSetting.vue';
import ActivityCalendarAbstractSetting from './ActivityCalendarAbstractSetting.vue';

const { t } = useI18n();

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

</script>

<style scoped lang="less">
.el-card {
    --el-card-padding: 10px;
}

.dot {
    height: 12px;
    width: 12px;
    border-radius: 50%;
    display: inline-block;
}
</style>