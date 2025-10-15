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
    <div v-else class="cell" :style="{ backgroundColor: color, color: fontColor }">
        <el-text>{{ defaultVideos[level][displayBy] }}</el-text>
    </div>
</template>

<script setup lang="ts">
import { VideoAbstract } from '@/utils/videoabstract';
import { computed, PropType } from 'vue';
import { Tippy } from 'vue-tippy';
import { ElLink, ElText } from 'element-plus';
import { MS_Level } from '@/utils/ms_const';
import { getTextColor, PiecewiseColorScheme } from '@/utils/colors';
import tinycolor from 'tinycolor2';
import { preview } from '@/utils/common/PlayerDialog';
import BaseCardSmall from '@/components/common/BaseCardSmall.vue';
import VideoAbstractDisplay from '@/components/widgets/VideoAbstractDisplay.vue';
import { defaultVideos } from './utils';

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
    --el-link-font-size: 16px;
}

</style>
