<template>
    <div class="cell">
        <el-text>
            {{ t(`common.prop.${sortBy}`) }}
        </el-text>
    </div>
    <Cell v-for="video in sortedVideos" :key="video.id" :video="video" :level="video.level" :color-theme="colorScheme" :display-by="sortBy" />
    <Cell v-for="i in count - sortedVideos.length" :key="i" :level="level" :color-theme="colorScheme" :display-by="sortBy" />
    <div class="cell" :style="{ backgroundColor: avgColor }">
        <el-text :style="{ color: avgFontColor }">
            {{ formatNumberSmart(sumStat, 6, 3) }}
        </el-text>
    </div>
</template>

<script setup lang="ts">
import { colorTheme } from '@/store';
import { getTextColor, PiecewiseColorScheme } from '@/utils/colors';
import { MS_Level } from '@/utils/ms_const';
import { VideoAbstract } from '@/utils/videoabstract';
import { computed, PropType } from 'vue';
import Cell from './Cell.vue';
import { useI18n } from 'vue-i18n';
import { sum } from 'd3-array';
import { defaultVideos } from './utils';
import tinycolor from 'tinycolor2';
import { formatNumberSmart } from '@/utils/strings';
import { ElText } from 'element-plus';

type sortByOptions = 'time' | 'bvs' | 'stnb';

const { t } = useI18n();

const props = defineProps({
    videos: {
        type: Array as PropType<VideoAbstract[]>,
        default: () => [],
    },
    level: {
        type: String as PropType<MS_Level>,
        required: true,
    },
    sortBy: {
        type: String as PropType<sortByOptions>,
        required: true,
    },
    count: {
        type: Number,
        required: true,
    },
});

const colorScheme = computed(() => {
    switch (props.sortBy) {
        case 'time':
            return PiecewiseColorScheme.createFromTheme(colorTheme.value[`${props.level}time`]);
        case 'bvs':
            return PiecewiseColorScheme.createFromTheme(colorTheme.value.bvs);
        case 'stnb':
            return PiecewiseColorScheme.createFromTheme(colorTheme.value.stnb);
        default:
            throw new Error('Invalid sortBy option');
    }
});

const sortedVideos = computed(() => {
    const sorted = Array.from(props.videos).sort((v1, v2) => v1.getStat(props.sortBy)! - v2.getStat(props.sortBy)!);
    if (props.sortBy === 'time') {
        return sorted.slice(0, props.count);
    } else {
        return sorted.slice(-props.count).reverse();
    }
});

const sumStat = computed(() => {
    return sum(sortedVideos.value, (video) => video.getStat(props.sortBy)!) + (props.count - sortedVideos.value.length) * defaultVideos[props.level][props.sortBy];
});

const avgStat = computed(() => {
    return sumStat.value / props.count;
});

const avgColor = computed(() => {
    return colorScheme.value.getColor(avgStat.value);
});

const avgFontColor = computed(() => {
    const tc = tinycolor(avgColor.value);
    return tc.getAlpha() == 0 ? getTextColor() : tc.isDark() ? 'white' : 'black';
});

defineExpose({
    sumStat,
});

</script>

<style lang="less" scoped>

@import './cell.less';

</style>
