<template>
    <el-text
        :style="{
            display: 'inline-block',
            fontSize: `${cellFullSize - 8}px`,
            lineHeight: `${cellFullSize}px`,
            marginTop: '0',
            marginRight: `${activityCalendarConfig.cellMargin}px`,
        }"
    >
        <IconSetting>
            <Setting />
        </IconSetting><br>
        Sun<br>Mon<br>Tue<br>Wed<br>Thu<br>Fri<br>Sat
    </el-text>
</template>

<script setup lang="ts">
import { activityCalendarConfig } from '@/store';
import { computed } from 'vue';
import { ElText } from 'element-plus';
import IconSetting from '@/components/widgets/IconSetting.vue';
import Setting from './Setting.vue';

const cellFullSize = computed(() => activityCalendarConfig.value.cellSize + activityCalendarConfig.value.cellMargin);

</script>
