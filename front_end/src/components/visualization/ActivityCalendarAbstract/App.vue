<template>
    <BaseCardNormal style="overflow: auto;">
        <ElRow style="align-items: center; display: flex; margin-bottom: 5px;">
            <Header data-cy="header" :video-list="videoList" />
        </ElRow>
        <ElRow>
            <DayLabel data-cy="dayLabel" :cell-size="options.cellSize" :cell-margin="options.cellMargin" />
            <ElScrollbar style="flex:1;">
                <ElRow :style="{ height: `${cellFullSize}px` }">
                    <MonthLabel :start-date="startDate" :end-date="endDate" :cell-size="options.cellSize" :cell-margin="options.cellMargin" />
                </ElRow>
                <ElRow :style="{ height: `${cellFullSize * 7 + options.cellMargin}px` }">
                    <Tippy
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
                            v-for="cell of dateCells"
                            :key="cell.dateKey"
                            class="calendar-cell text"
                            :style="{
                                width: `${options.cellSize}px`,
                                height: `${options.cellSize}px`,
                                fontSize: `${options.cellSize * 0.6}px`,
                            }"
                            :data-cy="`cell-${cell.dateKey}`"
                            @mouseover="tooltipVideos = cell.videos; tooltipDate = cell.date"
                        >
                            <MiniPie
                                v-if="cell.pieData.length > 0"
                                class="mini-pie"
                                :data="cell.pieData"
                                :radius="options.cellSize / 2"
                                :stroke-width="0"
                            />
                            <span v-if="options.showDate" class="date-label">
                                {{ cell.date.getDate() }}
                            </span>
                        </div>
                        <template #content>
                            <Tooltip :date="tooltipDate" :videos="tooltipVideos" />
                        </template>
                    </Tippy>
                </ElRow>
            </ElScrollbar>
        </ElRow>
    </BaseCardNormal>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { MiniPie } from '@putianyi888/vue3-plots';
import type { PieDatum } from '@putianyi888/vue3-plots';
import { ElRow, ElScrollbar } from 'element-plus';
import type { PropType } from 'vue';
import { computed, ref } from 'vue';
import { Tippy } from 'vue-tippy';

import DayLabel from './DayLabel.vue';
import Header from './Header.vue';
import MonthLabel from './MonthLabel.vue';
import Tooltip from './Tooltip.vue';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import { colorTheme } from '@/store';
import { generateDateRange, toISODateString } from '@/utils/datetime';
import { isStandardLevel } from '@/utils/ms_const';
import type { VideoAbstract } from '@/utils/videoabstract';
import { groupVideosByDate } from '@/utils/videoabstract';

interface Options {
    cellSize: number;
    cellMargin: number;
    showDate: boolean;
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
                useEndTime: false,
            };
        },
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

const dateRange = computed(() => Array.from(generateDateRange(startDate.value, endDate, 1)));
const dateCells = computed(() => dateRange.value.map((date) => {
    const dateKey = toISODateString(date);
    const videos = groupedVideoAbstract.value.get(dateKey) ?? [];
    return {
        date,
        dateKey,
        videos,
        pieData: getPieData(videos),
    };
}));

function getPieData(videos: VideoAbstract[]): PieDatum[] {
    const count = { b: 0, i: 0, e: 0, c: 0 };
    for (const video of videos) {
        if (isStandardLevel(video.level)) count[video.level]++;
        else count.c++;
    }
    return [
        { value: count.b, color: colorTheme.value.level.b },
        { value: count.i, color: colorTheme.value.level.i },
        { value: count.e, color: colorTheme.value.level.e },
        { value: count.c, color: colorTheme.value.level.c },
    ].filter((data) => data.value > 0);
}
</script>

<style scoped>
.calendar-cell {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
}

.mini-pie {
    position: absolute;
    inset: 0;
}

.date-label {
    position: relative;
    z-index: 1;
}
</style>
