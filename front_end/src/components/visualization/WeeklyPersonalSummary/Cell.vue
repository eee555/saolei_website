<template>
    <Tippy v-if="video" class="cell" :style="{ backgroundColor: color }" :duration="0" sticky>
        <ElLink underline="never" @click="preview(video.id)">
            {{ video.displayStat('time') }}
        </ElLink>
        <template #content>
            <ElCard v-if="video" class="card-small">
                <VideoAbstractDisplay :video="video" />
            </ElCard>
        </template>
    </Tippy>
    <div v-else class="cell" :style="{ backgroundColor: color }">
        <span class="text" :style="{ color: fontColor }">
            {{ defaultTime }}
        </span>
    </div>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import '@/styles/cards.css';

import { ElCard, ElLink } from 'element-plus';
import tinycolor from 'tinycolor2';
import type { PropType } from 'vue';
import { computed } from 'vue';
import { Tippy } from 'vue-tippy';

import VideoAbstractDisplay from '@/components/widgets/VideoAbstractDisplay.vue';
import { getTextColor, PiecewiseColorScheme } from '@/utils/colors';
import { preview } from '@/utils/common/PlayerDialog';
import type { VideoAbstract } from '@/utils/videoabstract';

const props = defineProps({
    video: { type: Object as PropType<VideoAbstract | undefined>, default: undefined },
    colorTheme: { type: Object as PropType<PiecewiseColorScheme>, default: new PiecewiseColorScheme([], []) },
    defaultTime: { type: Number, default: 240 },
});

const color = computed(() => {
    if (!props.video) return props.colorTheme.getColor(props.defaultTime);
    return props.colorTheme.getColor(props.video.time);
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
