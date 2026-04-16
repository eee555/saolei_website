<template>
    <base-card-normal style="overflow: auto;">
        <el-row style="align-items: center; display: flex; margin-bottom: 5px;">
            <Header data-cy="header" :video-list="videoList" />
        </el-row>
        <el-row>
            <DayLabel data-cy="dayLabel" :cell-size="options.cellSize" :cell-margin="options.cellMargin" />
            <el-scrollbar style="flex:1;">
                <el-row :style="{ height: `${cellFullSize}px` }">
                    <MonthLabel :start-date="startDate" :end-date="endDate" :cell-size="options.cellSize" :cell-margin="options.cellMargin" />
                </el-row>
                <el-row
                    :style="{
                        height: `${cellFullSize * 7 + options.cellMargin}px`,
                        filter: `invert(${darkMode ? 0 : 1})`,
                    }"
                >
                    <tippy
                        :duration="0"
                        sticky
                        follow-cursor
                        :style="{
                            height: '100%',
                            display: 'grid',
                            gridTemplateRows: 'repeat(7, 1fr)',
                            gridAutoFlow: 'column',
                            gap: `${options.cellMargin}px`,
                        }"
                    >
                        <!-- 为每个日期生成一个单元格 -->
                        <div :style="{gridRowStart: `${startDate.getDay()}`}" />
                        <div
                            v-for="date of dateRange"
                            :key="date.toISOString()"
                            class="text"
                            :style="{
                                width: `${options.cellSize}px`,
                                height: `${options.cellSize}px`,
                                borderRadius: `${options.cornerRadius}%`,
                                backgroundColor: getColor(groupedVideoAbstract.get(toISODateString(date)) || []),
                                display: 'flex',
                                justifyContent: 'center',
                                fontSize: `${options.cellSize * 0.6}px`,
                            }"
                            :data-cy="`cell-${toISODateString(date)}`"
                            @mouseover="tooltipVideos = groupedVideoAbstract.get(toISODateString(date)) || []; tooltipDate = date"
                        >
                            <template v-if="options.showDate">
                                {{ date.getDate() }}
                            </template>
                        </div>
                        <template #content>
                            <Tooltip :date="tooltipDate" :videos="tooltipVideos" />
                        </template>
                    </tippy>
                </el-row>
            </el-scrollbar>
        </el-row>
    </base-card-normal>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { ElRow, ElScrollbar } from 'element-plus';
import { computed, PropType, ref } from 'vue';
import { Tippy } from 'vue-tippy';

import DayLabel from './DayLabel.vue';
import Header from './Header.vue';
import MonthLabel from './MonthLabel.vue';
import Tooltip from './Tooltip.vue';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import { toISODateString } from '@/utils/datetime';
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

function *generateDateRange(startDate: Date, endDate: Date, step: number = 1) {
    const currentDate = new Date(startDate);
    while (currentDate <= endDate) {
        yield new Date(currentDate);  // Yield a new Date object (to avoid modifying the original one)
        currentDate.setDate(currentDate.getDate() + step); // Increment by 1 day (or custom step)
    }
}

const dateRange = computed(() => Array.from(generateDateRange(startDate.value, endDate, 1)));

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
