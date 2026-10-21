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
import { useTemplateRef, watch } from 'vue';

import Canvas from './Canvas.vue';
import { VideoScatterStore } from './store';
import Toolbar from './Toolbar.vue';

import type { VideoAbstract } from '@/utils/videoabstract';

const props = defineProps({
    videos: { type: Array<VideoAbstract>, default: () => [] },
});

const scatterRef = useTemplateRef<HTMLDivElement>('scatterRef');
const { isFullscreen, toggle } = useFullscreen(scatterRef);

type TippyHost = HTMLElement & { _tippy?: { popper?: HTMLElement } };

// tippy 只在浮层首次显示时挂载 DOM，之后再进/出全屏不会重新挂载。
// 这里把已经存在的浮层跟着搬进全屏子树，退出时搬回 body。
watch(isFullscreen, (fullscreen) => {
    const root = scatterRef.value;
    if (!root) return;
    const target = fullscreen ? root : document.body;
    root.querySelectorAll<TippyHost>('.video-scatter-tippy, .marker-setting-tippy').forEach((element) => {
        const popper: HTMLElement | undefined = element._tippy?.popper;
        if (popper !== undefined && popper.parentElement !== target) target.appendChild(popper);
    });
});

watch(() => props.videos, (videos) => {
    VideoScatterStore.setRawData(videos);
}, { immediate: true });
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
    background: var(--ui-bg-color);
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
