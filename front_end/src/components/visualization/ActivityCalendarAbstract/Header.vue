<template>
    <div data-cy="count" style="display: flex; width: 100%; align-items: center">
        <span class="text text-small" style="margin-right: 0.5em">
            {{ t('local.totalNVideos', [videoList.length]) }}
        </span>
        <div style="flex-grow: 1;">
            <StackBar :data="videoCountData" style="flex: 1;" />
        </div>
    </div>
    <div data-cy="size" style="display: flex; width: 100%; align-items: center">
        <span class="text text-small" style="margin-right: 0.5em">
            {{ t('local.totalNBytes', [begSize + intSize + expSize]) }}
        </span>
        <div style="flex-grow: 1;">
            <StackBar :data="videoFileSizeDate" />
        </div>
    </div>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import Lazy from 'lazy.js';
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

import StackBar from '@/components/visualization/StackBar/App.vue';
import { VideoAbstract } from '@/utils/videoabstract';

const prop = defineProps({
    videoList: {
        type: Array<VideoAbstract>,
        default: () => [],
    },
});

const begCount = computed(() => {
    return Lazy(prop.videoList).filter((v) => v.level == 'b').size();
});
const intCount = computed(() => {
    return Lazy(prop.videoList).filter((v) => v.level == 'i').size();
});
const expCount = computed(() => {
    return Lazy(prop.videoList).filter((v) => v.level == 'e').size();
});

const begSize = computed(() => {
    return Lazy(prop.videoList).filter((v) => v.level == 'b').sum((v) => v.file_size);
});
const intSize = computed(() => {
    return Lazy(prop.videoList).filter((v) => v.level == 'i').sum((v) => v.file_size);
});
const expSize = computed(() => {
    return Lazy(prop.videoList).filter((v) => v.level == 'e').sum((v) => v.file_size);
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

/* 本地化 Localization */
const i18nMessages = {
    'zh-cn': { local: {
        totalNBytes: '占用{0}字节',
        totalNVideos: '共{0}个录像',
    } },
    'en': { local: {
        totalNBytes: '{0} bytes',
        totalNVideos: '{0} videos in total',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>

<style scoped lang="less">

.dot {
    height: 12px;
    width: 12px;
    border-radius: 50%;
    display: inline-block;
}

</style>
