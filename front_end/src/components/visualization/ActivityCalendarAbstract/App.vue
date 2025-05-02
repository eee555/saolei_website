<template>
    <base-card-normal style="overflow: auto;">
        <el-row style="align-items: center; display: flex; margin-bottom: 5px;">
            <Header data-cy="header" :video-list="videoList" />
        </el-row>
        <el-row>
            <DayLabel data-cy="dayLabel" :cell-size="options.cellSize" :cell-margin="options.cellMargin" />
            <el-scrollbar style="flex:1;">
                <el-row>
                    <MonthLabel :start-date="startDate" :end-date="endDate" :cell-size="options.cellSize" :cell-margin="options.cellMargin" />
                </el-row>
                <el-row
                    :style="{
                        position: 'relative',
                        height: `${cellFullSize * 8 + options.cellMargin}px`,
                        filter: `invert(${darkMode ? 0 : 1})`,
                    }"
                >
                    <template v-for="date of generateDateRange(startDate, endDate)" :key="date.toISOString()">
                        <Cell
                            :data-cy="`cell-${toISODateString(date)}`"
                            :date="date" :start-date="startDate"
                            :videos="groupedVideoAbstract.get(toISODateString(date))"
                            :x-offset="Math.round((getWeekTime(date) - startWeekTime) / fullWeek)"
                            :y-offset="date.getDay() + 1" :show-date="options.showDate" :cell-size="options.cellSize" :cell-margin="options.cellMargin" :corner-radius="options.cornerRadius"
                        />
                    </template>
                </el-row>
            </el-scrollbar>
        </el-row>
    </base-card-normal>
</template>

<script setup lang="ts">

import { computed, defineAsyncComponent, PropType } from 'vue';
import { groupVideosByUploadDate, VideoAbstract } from '@/utils/videoabstract';
import { fullWeek, getWeekTime, toISODateString } from '@/utils/datetime';
import { ElRow, ElScrollbar } from 'element-plus';
import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import Header from './Header.vue';
import DayLabel from './DayLabel.vue';
import MonthLabel from './MonthLabel.vue';
const Cell = defineAsyncComponent(() => import('./Cell.vue'));

interface Options {
    cellSize: number;
    cellMargin: number;
    showDate: boolean;
    cornerRadius: number;
}

const props = defineProps({
    videoList: {
        type: Array<VideoAbstract>,
        default: () => [],
    },
    options: {
        type: Object as PropType<Options>,
        default: () => {
            return {
                cellSize: 14,
                cellMargin: 3,
                showDate: true,
                cornerRadius: 20,
            };
        },
    },
    darkMode: {
        type: Boolean,
        default: true,
    },
});

const cellFullSize = computed(() => props.options.cellSize + props.options.cellMargin);

const groupedVideoAbstract = computed(() => groupVideosByUploadDate(props.videoList));
const endDate = new Date(new Date().toDateString()); // today
const startDate = computed(() => {
    const keys = groupedVideoAbstract.value.keys();
    let min = new Date(endDate);
    min.setFullYear(min.getFullYear() - 1);
    min.setDate(min.getDate() + 1);
    for (const key of keys) {
        const keydate = new Date(key);
        if (keydate < min) min = keydate;
    }
    return min;
});
const startWeekTime = computed(() => getWeekTime(startDate.value));

function *generateDateRange(startDate: Date, endDate: Date, step: number = 1) {
    const currentDate = new Date(startDate);
    while (currentDate <= endDate) {
        yield new Date(currentDate);  // Yield a new Date object (to avoid modifying the original one)
        currentDate.setDate(currentDate.getDate() + step); // Increment by 1 day (or custom step)
    }
}

</script>
