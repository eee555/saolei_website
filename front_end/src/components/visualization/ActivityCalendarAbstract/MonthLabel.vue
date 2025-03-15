<template>
    <el-text v-for="date of generateMonthLabelRange(startDate, endDate)" :style="{
        position: 'absolute',
        fontSize: '12px',
        top: 0,
        left: (date.getTime() - startWeekTime) / fullWeek * cellFullSize + 'px',
        transform: 'translate(-50%,0)'
    }">{{ monthNameShort[date.getMonth()] }}</el-text>
</template>

<script setup lang="ts">
import { activityCalendarConfig } from '@/store';
import { fullWeek, getWeekTime, monthNameShort } from '@/utils/datetime';
import { computed } from 'vue';
import { ElText } from 'element-plus';

const prop = defineProps({
    startDate: { type: Date, required: true },
    endDate: { type: Date, required: true },
})

const startWeekTime = computed(() => getWeekTime(prop.startDate));
const cellFullSize = computed(() => activityCalendarConfig.value.cellSize + activityCalendarConfig.value.cellMargin);

function generateMonthLabelRange(startDate: Date, endDate: Date) {
    let currentDate = new Date(startDate);
    if (currentDate.getDate() > 15) {
        currentDate.setMonth(currentDate.getMonth() + 1);
        currentDate.setDate(15);
    }
    const monthLabels = [];
    while (currentDate <= endDate) {
        monthLabels.push(currentDate);
        currentDate = new Date(currentDate);
        currentDate.setMonth(currentDate.getMonth() + 1);
    }
    return monthLabels;
}

</script>