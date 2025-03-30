<template>
    <el-text 
        :style="{
            display: 'inline-block',
            fontSize: `${cellFullSize - 8}px`,
            lineHeight: `${cellFullSize}px`,
            marginTop: `${cellFullSize}px`,
            marginRight: `${activityCalendarConfig.cellMargin}px`,
        }"
    >
        Sun<br>Mon<br>Tue<br>Wed<br>Thu<br>Fri<br>Sat
    </el-text>
</template>

<script setup lang="ts">
import { activityCalendarConfig } from '@/store';
import { computed } from 'vue';
import { ElText } from 'element-plus';

const cellFullSize = computed(() => activityCalendarConfig.value.cellSize + activityCalendarConfig.value.cellMargin);

</script>
