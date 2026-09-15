<template>
    <Tippy v-if="video" class="cell" :style="cellStyle" :duration="0" sticky>
        <ElLink underline="never" @click="preview(video.id)">
            {{ video.displayStat('time') }}
        </ElLink>
        <template #content>
            <ElCard v-if="video" class="card-small">
                <VideoAbstractDisplay :video="video" />
            </ElCard>
        </template>
    </Tippy>
    <div v-else class="cell" :style="cellStyle">
        <span class="text">
            {{ defaultTime }}
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

import VideoAbstractDisplay from '@/components/widgets/VideoAbstractDisplay.vue';
import { PiecewiseColorScheme } from '@/utils/colors';
import { preview } from '@/utils/common/PlayerDialog';
import type { VideoAbstract } from '@/utils/videoabstract';

const props = defineProps({
    video: { type: Object as PropType<VideoAbstract | undefined>, default: undefined },
    colorTheme: { type: Object as PropType<PiecewiseColorScheme>, default: new PiecewiseColorScheme([], []) },
    defaultTime: { type: Number, default: 240 },
});

const cellStyle = computed(() => {
    if (!props.video) return props.colorTheme.getStyle(props.defaultTime);
    return props.colorTheme.getStyle(props.video.time);
});
</script>

<style lang="less" scoped>
@import './cell.less';

.el-link {
    --el-link-text-color: currentColor;
}
</style>
