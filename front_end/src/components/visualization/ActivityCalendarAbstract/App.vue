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
                    <base-tooltip :show-animation="0" :hide-animation="0" sticky follow-cursor>
                        <!-- 为每个日期生成一个单元格 -->
                        <template v-for="date of generateDateRange(startDate, endDate)" :key="date.toISOString()">
                            <span
                                :style="{
                                    position: 'absolute',
                                    top: `${(date.getDay() + 1) * cellFullSize}px`,
                                    left: `${Math.round((getWeekTime(date) - startWeekTime) / fullWeek) * cellFullSize}px`,
                                    width: `${options.cellSize}px`,
                                    height: `${options.cellSize}px`,
                                    borderRadius: `${options.cornerRadius}%`,
                                    backgroundColor: getColor(groupedVideoAbstract.get(toISODateString(date)) || []),
                                }"
                                :data-cy="`cell-${toISODateString(date)}`"
                                @mouseover="tooltipVideos = groupedVideoAbstract.get(toISODateString(date)) || []; tooltipDate = date"
                            >
                                <el-text
                                    v-if="options.showDate"
                                    :style="{
                                        position: 'absolute',
                                        top: '50%',
                                        left: '50%',
                                        transform: 'translate(-50%, -50%)',
                                        fontSize: `${options.cellSize * 0.6}px`,
                                        color: darkMode ? '#fff' : '#000',
                                    }"
                                >
                                    {{ date.getDate() }}
                                </el-text>
                            </span>
                        </template>
                        <template #content>
                            <Tooltip :date="tooltipDate" :videos="tooltipVideos" />
                        </template>
                    </base-tooltip>
                </el-row>
            </el-scrollbar>
        </el-row>
    </base-card-normal>
</template>

<script setup lang="ts">

import { ElRow, ElScrollbar, ElText } from 'element-plus';
import { computed, PropType, ref } from 'vue';

import DayLabel from './DayLabel.vue';
import Header from './Header.vue';
import MonthLabel from './MonthLabel.vue';
import Tooltip from './Tooltip.vue';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import BaseTooltip from '@/components/common/BaseTooltip.vue';
import { fullWeek, getWeekTime, toISODateString } from '@/utils/datetime';
import { groupVideosByDate, VideoAbstract } from '@/utils/videoabstract';

interface Options {
    cellSize: number;
    cellMargin: number;
    showDate: boolean;
    cornerRadius: number;
    useEndTime: boolean;
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
                useEndTime: false,
            };
        },
    },
    darkMode: {
        type: Boolean,
        default: true,
    },
});

const tooltipVideos = ref([] as VideoAbstract[]);
const tooltipDate = ref(new Date());

const cellFullSize = computed(() => props.options.cellSize + props.options.cellMargin);

const groupedVideoAbstract = computed(() => groupVideosByDate(props.videoList, props.options.useEndTime ? 'end_time' : 'upload_time'));
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

function getColor(videos: VideoAbstract[]) {
    let red = 0, green = 0, blue = 0;
    for (const video of videos) {
        if (video.level === 'b') red++;
        else if (video.level === 'i') green++;
        else if (video.level === 'e') blue++;
    }
    return `rgb(${Math.min(255, red * 51)}, ${Math.min(255, green * 51)}, ${Math.min(255, blue * 51)})`;
}

</script>
