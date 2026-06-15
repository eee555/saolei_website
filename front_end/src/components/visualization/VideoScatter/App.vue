<template>
    <div ref="scatterRef" class="video-scatter" :class="{ 'is-fullscreen': isFullscreen }">
        <Toolbar :is-fullscreen="isFullscreen" @toggle-fullscreen="toggle" />
        <div class="video-scatter-canvas">
            <Canvas />
        </div>
    </div>
</template>

<script setup lang="ts">
import { useFullscreen } from '@vueuse/core';
import { ref, watch } from 'vue';

import Canvas from './Canvas.vue';
import { VideoScatterStore } from './store';
import Toolbar from './Toolbar.vue';

import type { VideoAbstract } from '@/utils/videoabstract';

const props = defineProps({
    videos: { type: Array<VideoAbstract>, default: () => [] },
});

const scatterRef = ref<HTMLElement>();
const { isFullscreen, toggle } = useFullscreen(scatterRef);

watch(() => props.videos, VideoScatterStore.setRawData, { immediate: true });
</script>

<style lang="less" scoped>
.video-scatter {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    gap: 1em;
    height: 600px;
}

.video-scatter.is-fullscreen {
    background: var(--el-bg-color);
    box-sizing: border-box;
    height: 100vh;
    padding: 1em;
    width: 100vw;
}

.video-scatter-canvas {
    display: flex;
    flex: 1 1 auto;
    min-height: 0;
}
</style>
