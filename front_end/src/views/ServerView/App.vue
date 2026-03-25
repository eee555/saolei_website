<template>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(19rem, auto)); grid-gap: 1rem;">
        <TaskSummary />
        <VideoSummary />
    </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent } from 'vue';

const TaskSummary = defineAsyncComponent(() => import('./TaskSummary.vue'));
const VideoSummary = defineAsyncComponent(() => import('./VideoSummary.vue'));
</script>
