<template>
    <Scatter
        :points="selectedSeries.points"
        :fill-color="selectedSeries.colors"
        :opacity="0.3" :radius="10"
    />
</template>

<script setup lang="ts">
import type { PlotPoint } from '@putianyi888/vue3-plots';
import { Scatter } from '@putianyi888/vue3-plots';
import { computed } from 'vue';

import { VideoScatterStore } from './store';

import type { VideoAbstract } from '@/utils/videoabstract';

const selectedSeries = computed(() => {
    const points = [] as PlotPoint<VideoAbstract>[];
    const colors = [] as string[];

    for (let i = 0; i < VideoScatterStore.scatterData.indices.length; i++) {
        if (VideoScatterStore.selectedFlags[VideoScatterStore.scatterData.indices[i]]) {
            points.push(VideoScatterStore.scatterData.points[i]);
            colors.push(VideoScatterStore.fillColor[i]);
        }
    }

    return { points, colors };
});
</script>
