<template>
    <el-text v-t="{ path: 'activityCalendar.totalNVideos', args: [store.player.videos.length] }" size="small" />
    <span style="flex: 1;"></span>
    <span class="dot" style=" background-color: #f00;" />
    <el-text v-t="'common.level.shortb'" size="small" />&nbsp;
    <span class="dot" style=" background-color: #080;" />
    <el-text v-t="'common.level.shorti'" size="small" />&nbsp;
    <span class="dot" style=" background-color: #00f;" />
    <el-text v-t="'common.level.shorte'" size="small" />
    <span style="width: 10px;"></span>
    <IconSetting>
        <Setting />
    </IconSetting>
</template>

<script setup lang="ts">
import { store } from '@/store';
import { ElText } from 'element-plus';
import Setting from './Setting.vue';
import IconSetting from '@/components/widgets/IconSetting.vue';

</script>

<style scoped lang="less">

.dot {
    height: 12px;
    width: 12px;
    border-radius: 50%;
    display: inline-block;
}

</style>