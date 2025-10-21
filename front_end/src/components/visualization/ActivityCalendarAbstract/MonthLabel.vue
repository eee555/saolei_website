<template>
    <el-text
        v-for="date of generateMonthLabelRange(startDate, endDate)" :key="date.toISOString()" :style="{
            position: 'absolute',
            fontSize: '12px',
            top: 0,
            left: `${(date.getTime() - startWeekTime) / fullWeek * cellFullSize}px`,
            transform: 'translate(-50%,0)'
        }"
    >
        {{ monthNameShort[date.getMonth()] }}
    </el-text>
</template>

<script setup lang="ts">
import { ElText } from 'element-plus';
import { computed } from 'vue';

import { fullWeek, getWeekTime, monthNameShort } from '@/utils/datetime';

const prop = defineProps({
    startDate: { type: Date, required: true },
    endDate: { type: Date, required: true },
    cellSize: { type: Number, default: 14 }, // 格子大小，单位为px
    cellMargin: { type: Number, default: 3 }, // 格子间距，单位为px
});

const startWeekTime = computed(() => getWeekTime(prop.startDate));
const cellFullSize = computed(() => prop.cellSize + prop.cellMargin);

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
