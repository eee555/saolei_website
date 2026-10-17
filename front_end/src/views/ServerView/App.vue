<template>
    <MasonryLayout class="server-statistics">
        <div data-statistic-item="disk">
            <DiskUsage />
        </div>
        <div data-statistic-item="process">
            <MemoryUsage :section="memoryUsage?.memory" :loading="memoryLoading" :failed="memoryFailed" @refresh="refreshMemory" />
        </div>
        <div data-statistic-item="redis">
            <RedisMemoryUsage :section="memoryUsage?.redis" :loading="memoryLoading" :failed="memoryFailed" @refresh="refreshMemory" />
        </div>
        <div data-statistic-item="tasks">
            <TaskSummary />
        </div>
        <div data-statistic-item="videos">
            <VideoSummary />
        </div>
        <div data-statistic-item="top">
            <TopAnchors />
        </div>
    </MasonryLayout>
</template>

<script setup lang="ts">
import { defineAsyncComponent, onBeforeUnmount, onMounted, ref } from 'vue';

import type { MemoryUsageResponse } from './memory';
import MemoryUsage from './MemoryUsage.vue';
import RedisMemoryUsage from './RedisMemoryUsage.vue';

import MasonryLayout from '@/components/common/MasonryLayout.vue';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

const DiskUsage = defineAsyncComponent(() => import('./DiskUsage.vue'));
const TaskSummary = defineAsyncComponent(() => import('./TaskSummary.vue'));
const VideoSummary = defineAsyncComponent(() => import('./VideoSummary.vue'));
const TopAnchors = defineAsyncComponent(() => import('./TopAnchors.vue'));

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
