<template>
    <Tippy v-if="video" class="cell" :style="cellStyle" :duration="0" sticky>
        <ElLink underline="never" @click="preview(video.id)">
            {{ video.displayStat(displayBy) }}
        </ElLink>
        <template #content>
            <ElCard v-if="video" class="card-small">
                <VideoAbstractDisplay :video="video" />
            </ElCard>
        </template>
    </Tippy>
    <div v-else class="cell" :style="cellStyle">
        <span class="text">
            {{ defaultVideos[level][displayBy] }}
        </span>
    </div>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import '@/styles/cards.css';

import { ElCard, ElLink } from 'element-plus';
import type { PropType } from 'vue';
import { computed } from 'vue';
import { Tippy } from 'vue-tippy';

import { defaultVideos } from './utils';

import VideoAbstractDisplay from '@/components/widgets/VideoAbstractDisplay.vue';
import { PiecewiseColorScheme } from '@/utils/colors';
import { preview } from '@/utils/common/PlayerDialog';
import type { MS_Level } from '@/utils/ms_const';
import type { VideoAbstract } from '@/utils/videoabstract';

type sortByOption = 'time' | 'bvs' | 'stnb';

const props = defineProps({
    level: { type: String as PropType<MS_Level>, required: true },
    video: { type: Object as PropType<VideoAbstract | undefined>, default: undefined },
    displayBy: { type: String as PropType<sortByOption>, default: 'time' },
    colorTheme: { type: Object as PropType<PiecewiseColorScheme>, default: new PiecewiseColorScheme([], []) },
});

const cellStyle = computed(() => {
    if (!props.video) return props.colorTheme.getStyle(defaultVideos[props.level][props.displayBy]);
    return props.colorTheme.getStyle(props.video[props.displayBy]);
});
</script>

<style lang="less" scoped>
@import './cell.less';

.el-link {
    --el-link-text-color: currentColor;
}
</style>
