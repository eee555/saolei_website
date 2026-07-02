<template>
    <div data-cy="count" style="display: flex; width: 100%; align-items: center">
        <span class="text text-small" style="margin-right: 0.5em">
            {{ t('local.totalNVideos', [videoList.length]) }}
        </span>
        <div style="flex-grow: 1;">
            <StackBar :data="videoCountData" />
        </div>
    </div>
    <div data-cy="size" style="display: flex; width: 100%; align-items: center">
        <span class="text text-small" style="margin-right: 0.5em">
            {{ t('local.totalNBytes', [begSize + intSize + expSize + cusSize]) }}
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
import { colorTheme } from '@/store';
import type { VideoAbstract } from '@/utils/videoabstract';

const props = defineProps({
    videoList: {
        type: Array<VideoAbstract>,
        default: () => [],
    },
});

const begCount = computed(() => {
    return Lazy(props.videoList).filter((v) => v.level == 'b').size();
});
const intCount = computed(() => {
    return Lazy(props.videoList).filter((v) => v.level == 'i').size();
});
const expCount = computed(() => {
    return Lazy(props.videoList).filter((v) => v.level == 'e').size();
});
const cusCount = computed(() => {
    return Lazy(props.videoList).filter((v) => typeof v.level !== 'string').size();
});

const begSize = computed(() => {
    return Lazy(props.videoList).filter((v) => v.level == 'b').sum((v) => v.file_size);
});
const intSize = computed(() => {
    return Lazy(props.videoList).filter((v) => v.level == 'i').sum((v) => v.file_size);
});
const expSize = computed(() => {
    return Lazy(props.videoList).filter((v) => v.level == 'e').sum((v) => v.file_size);
});
const cusSize = computed(() => {
    return Lazy(props.videoList).filter((v) => typeof v.level !== 'string').sum((v) => v.file_size);
});

const videoCountData = computed(() => {
    return [
        { name: t('common.level.b'), value: begCount.value, color: colorTheme.value.level.b },
        { name: t('common.level.i'), value: intCount.value, color: colorTheme.value.level.i },
        { name: t('common.level.e'), value: expCount.value, color: colorTheme.value.level.e },
        { name: t('common.level.c'), value: cusCount.value, color: colorTheme.value.level.c },
    ];
});

const videoFileSizeDate = computed(() => {
    return [
        { name: t('common.level.b'), value: begSize.value, color: colorTheme.value.level.b },
        { name: t('common.level.i'), value: intSize.value, color: colorTheme.value.level.i },
        { name: t('common.level.e'), value: expSize.value, color: colorTheme.value.level.e },
        { name: t('common.level.c'), value: cusSize.value, color: colorTheme.value.level.c },
    ];
});

/* 本地化 Localization */
const i18nMessages = {
    'zh-cn': { local: {
        totalNBytes: '占用{0}字节',
        totalNVideos: '共{0}个录像',
    } },
    en: { local: {
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
