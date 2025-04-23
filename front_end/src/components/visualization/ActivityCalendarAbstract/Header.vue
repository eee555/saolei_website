<template>
    <el-row style="width: 100%; align-items: center">
        <el-text size="small" style="margin-right: 0.5em">
            {{ t('activityCalendar.totalNVideos', [store.player.videos.length]) }}
        </el-text>
        <StackBar :data="videoCountData" style="flex: 1;" />
    </el-row>
    <el-row style="width: 100%; align-items: center">
        <el-text size="small" style="margin-right: 0.5em">
            {{ t('activityCalendar.totalNBytes', [begSize + intSize + expSize]) }}
        </el-text>
        <StackBar :data="videoFileSizeDate" style="flex: 1;" />
    </el-row>
</template>

<script setup lang="ts">
import { store } from '@/store';
import { useI18n } from 'vue-i18n';
import 'vue-data-ui/style.css';
import Lazy from 'lazy.js';
import { computed } from 'vue';
import StackBar from '@/components/visualization/StackBar/App.vue';
import { ElText, ElRow } from 'element-plus';

const { t } = useI18n();

const begCount = computed(() => {
    return Lazy(store.player.videos).filter((v) => v.level == 'b').size();
});
const intCount = computed(() => {
    return Lazy(store.player.videos).filter((v) => v.level == 'i').size();
});
const expCount = computed(() => {
    return Lazy(store.player.videos).filter((v) => v.level == 'e').size();
});

const begSize = computed(() => {
    return Lazy(store.player.videos).filter((v) => v.level == 'b').sum((v) => v.file_size);
});
const intSize = computed(() => {
    return Lazy(store.player.videos).filter((v) => v.level == 'i').sum((v) => v.file_size);
});
const expSize = computed(() => {
    return Lazy(store.player.videos).filter((v) => v.level == 'e').sum((v) => v.file_size);
});

const videoCountData = computed(() => {
    return [
        { name: t('common.level.b'), value: begCount.value, color: '#FF0000' },
        { name: t('common.level.i'), value: intCount.value, color: '#008000' },
        { name: t('common.level.e'), value: expCount.value, color: '#0000FF' },
    ];
});

const videoFileSizeDate = computed(() => {
    return [
        { name: t('common.level.b'), value: begSize.value, color: '#FF0000' },
        { name: t('common.level.i'), value: intSize.value, color: '#008000' },
        { name: t('common.level.e'), value: expSize.value, color: '#0000FF' },
    ];
});

</script>

<style scoped lang="less">

.dot {
    height: 12px;
    width: 12px;
    border-radius: 50%;
    display: inline-block;
}

</style>
