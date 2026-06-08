<template>
    <div class="video-scatter">
        <Toolbar />
        <Canvas />
    </div>
</template>

<script setup lang="ts">
import { watch } from 'vue';

import Canvas from './Canvas.vue';
import { VideoScatterStore } from './store';
import Toolbar from './Toolbar.vue';

import type { VideoAbstract } from '@/utils/videoabstract';

const props = defineProps({
    videos: { type: Array<VideoAbstract>, default: () => [] },
});

watch(() => props.videos, VideoScatterStore.setRawData, { immediate: true });

</script>

<style lang="less" scoped>
.video-scatter {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    gap: 1em;
}
</style>
