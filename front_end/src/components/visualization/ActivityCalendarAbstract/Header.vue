<template>
    <el-text size="small" v-t="{ path: 'activityCalendar.totalNVideos', args: [store.player.videos.length] }" />
    <span style="flex: 1;"></span>
    <span class="dot" style=" background-color: #c00;" />
    <el-text size="small" v-t="'common.level.shortb'" />&nbsp;
    <span class="dot" style=" background-color: #0c0;" />
    <el-text size="small" v-t="'common.level.shorti'" />&nbsp;
    <span class="dot" style=" background-color: #00c;" />
    <el-text size="small" v-t="'common.level.shorte'" />
    <span style="width: 10px;"></span>
    <IconSetting>
        <Setting />
    </IconSetting>
</template>

<script setup lang="ts">
import { store } from '@/store';
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