<template>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(19rem, 100%), 1fr)); grid-gap: 1rem;">
        <DiskUsage />
        <MemoryUsage :section="memoryUsage?.memory" :loading="memoryLoading" :failed="memoryFailed" @refresh="refreshMemory" />
        <RedisMemoryUsage :section="memoryUsage?.redis" :loading="memoryLoading" :failed="memoryFailed" @refresh="refreshMemory" />
        <TaskSummary />
        <VideoSummary />
    </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent, onBeforeUnmount, onMounted, ref } from 'vue';

import type { MemoryUsageResponse } from './memory';
import MemoryUsage from './MemoryUsage.vue';
import RedisMemoryUsage from './RedisMemoryUsage.vue';

import useCurrentInstance from '@/utils/common/useCurrentInstance';

const DiskUsage = defineAsyncComponent(() => import('./DiskUsage.vue'));
const TaskSummary = defineAsyncComponent(() => import('./TaskSummary.vue'));
const VideoSummary = defineAsyncComponent(() => import('./VideoSummary.vue'));

const { proxy } = useCurrentInstance();
const memoryUsage = ref<MemoryUsageResponse | null>(null);
const memoryLoading = ref(false);
const memoryFailed = ref(false);
let memoryController: AbortController | null = null;

async function refreshMemory() {
    if (memoryLoading.value) return;
    memoryController = new AbortController();
    const { signal } = memoryController;
    memoryLoading.value = true;
    memoryFailed.value = false;
    try {
        const response = await proxy.$axios.get<MemoryUsageResponse>('/api/monitor/memoryusage', { signal });
        memoryUsage.value = response.data;
    } catch {
        if (!signal.aborted) memoryFailed.value = true;
    } finally {
        memoryLoading.value = false;
    }
}

onMounted(refreshMemory);
onBeforeUnmount(() => memoryController?.abort());
</script>
