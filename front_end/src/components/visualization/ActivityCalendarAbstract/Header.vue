<template>
    <el-text size="small">
        {{ t('activityCalendar.totalNVideos', [store.player.videos.length]) }}
    </el-text>
    <span style="flex: 1;" />
    <span class="dot" style=" background-color: #f00;" />
    <el-text size="small">
        {{ t('common.level.shortb') }}
    </el-text>&nbsp;
    <span class="dot" style=" background-color: #080;" />
    <el-text size="small">
        {{ t('common.level.shorti') }}
    </el-text>&nbsp;
    <span class="dot" style=" background-color: #00f;" />
    <el-text size="small">
        {{ t('common.level.shorte') }}
    </el-text>
    <span style="width: 10px;" />
    <IconSetting>
        <Setting />
    </IconSetting>
</template>

<script setup lang="ts">
import { store } from '@/store';
import { ElText } from 'element-plus';
import Setting from './Setting.vue';
import IconSetting from '@/components/widgets/IconSetting.vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

</script>

<style scoped lang="less">

.dot {
    height: 12px;
    width: 12px;
    border-radius: 50%;
    display: inline-block;
}

</style>