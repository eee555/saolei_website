<template>
    <Scatter
        :domain="VideoScatterStore.plotDomain"
        :size="VideoScatterStore.plotSize"
        :padding="VideoScatterStore.plotPadding"
        :points="selectedSeries.points"
        :fill-color="selectedSeries.colors"
        :opacity="0.3" :radius="10"
    />
</template>

<script setup lang="ts">
import { computed } from 'vue';

import { VideoScatterStore } from './store';

import { PlotPoint, Scatter } from '@/components/visualization/Plots';
import { VideoAbstract } from '@/utils/videoabstract';

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
