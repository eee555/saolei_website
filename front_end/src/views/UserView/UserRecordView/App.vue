<template>
    <div class="user-record-view">
        <ElSkeleton v-show="loading" animated style="margin-top: 0px;" :rows="8" />
        <SpeedCard :records="speedRecords" />
        <PLuckCard :records="pluckRecords" />
    </div>
</template>

<script lang="ts" setup>
import '@/styles/text.css';

import { ElMessage, ElSkeleton } from 'element-plus';
import { nextTick, ref } from 'vue';

import PLuckCard from './PLuckCard.vue';
import SpeedCard from './SpeedCard.vue';

import type { CustomPluckRecord } from '@/services/msuserService';
import { fetchCustomPluckPlayerRecords } from '@/services/msuserService';
import { fetchSpeedRecord } from '@/services/speedrankingService';
import type { SpeedBoard, SpeedRecord } from '@/services/speedrankingService';
import { store } from '@/store';

const loading = ref(true);
const pluckRecords = ref<CustomPluckRecord[]>([]);
const speedRecords = ref<Partial<Record<SpeedBoard, SpeedRecord>>>({});

// 此处和父组件配合，等一下从store里获取用户的id
void nextTick(() => {
    const playerId = store.player.id;
    const pluckRequest = fetchCustomPluckPlayerRecords(playerId).then((data) => {
        pluckRecords.value = data;
    }).catch(() => {
        ElMessage.error({ message: '自定义密度纪录加载失败', offset: 68 });
    });
    const boards: SpeedBoard[] = ['saolei', 'saolei_nf'];
    const speedRequests = boards.map(async (board) => {
        try {
            speedRecords.value[board] = await fetchSpeedRecord(playerId, board);
        } catch {
            ElMessage.error({ message: '竞速纪录加载失败', offset: 68 });
        }
    });
    void Promise.all([pluckRequest, ...speedRequests]).finally(() => {
        loading.value = false;
    });
});
</script>

<style scoped>
.user-record-view {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}
</style>
