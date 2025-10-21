<template>
    <tippy v-if="video" class="cell" :style="{ backgroundColor: color }" :duration="0" sticky>
        <el-link :underline="false" @click="preview(video.id)">
            {{ video.displayStat(displayBy) }}
        </el-link>
        <template #content>
            <base-card-small v-if="video">
                <video-abstract-display :video="video" />
            </base-card-small>
        </template>
    </tippy>
    <div v-else class="cell" :style="{ backgroundColor: color }">
        <el-text :style="{ color: fontColor }">
            {{ defaultVideos[level][displayBy] }}
        </el-text>
    </div>
</template>

<script setup lang="ts">
import { ElLink, ElText } from 'element-plus';
import tinycolor from 'tinycolor2';
import { computed, PropType } from 'vue';
import { Tippy } from 'vue-tippy';

import { defaultVideos } from './utils';

import BaseCardSmall from '@/components/common/BaseCardSmall.vue';
import VideoAbstractDisplay from '@/components/widgets/VideoAbstractDisplay.vue';
import { getTextColor, PiecewiseColorScheme } from '@/utils/colors';
import { preview } from '@/utils/common/PlayerDialog';
import { MS_Level } from '@/utils/ms_const';
import { VideoAbstract } from '@/utils/videoabstract';

type sortByOption = 'time' | 'bvs' | 'stnb';

const prop = defineProps({
    level: { type: String as PropType<MS_Level>, required: true },
    video: { type: Object as PropType<VideoAbstract | undefined>, default: undefined },
    displayBy: { type: String as PropType<sortByOption>, default: 'time' },
    colorTheme: { type: Object as PropType<PiecewiseColorScheme>, default: new PiecewiseColorScheme([], []) },
});

const color = computed(() => {
    if (!prop.video) return prop.colorTheme.getColor(defaultVideos[prop.level][prop.displayBy]);
    return prop.colorTheme.getColor(prop.video.getStat(prop.displayBy) as number);
});

const fontColor = computed(() => {
    const tc = tinycolor(color.value);
    return tc.getAlpha() == 0 ? getTextColor() : tc.isDark() ? 'white' : 'black';
});

</script>

<style lang="less" scoped>

@import './cell.less';

.el-link {
    --el-link-text-color: v-bind(fontColor);
}

</style>
