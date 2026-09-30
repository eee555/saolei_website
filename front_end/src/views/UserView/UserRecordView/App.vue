<template>
    <div class="user-record-view">
        <ElSkeleton v-show="loading" animated style="margin-top: 0px;" :rows="8" />
        <SaoleiCard :records="saoleiRecords" />
        <PLuckCard :records="pluckRecords" />
    </div>
</template>

<script lang="ts" setup>
import '@/styles/text.css';

import { ElMessage, ElSkeleton } from 'element-plus';
import { nextTick, ref } from 'vue';

import PLuckCard from './PLuckCard.vue';
import SaoleiCard from './SaoleiCard.vue';

import type { CustomPluckRecord } from '@/services/msuserService';
import { fetchCustomPluckPlayerRecords } from '@/services/msuserService';
import { fetchSaoleiRecord } from '@/services/saoleiRankingService';
import type { SaoleiBoard, SaoleiRecord } from '@/services/saoleiRankingService';
import { store } from '@/store';

const loading = ref(true);
const pluckRecords = ref<CustomPluckRecord[]>([]);
const saoleiRecords = ref<Partial<Record<SaoleiBoard, SaoleiRecord>>>({});

// 此处和父组件配合，等一下从store里获取用户的id
void nextTick(() => {
    const playerId = store.player.id;
    const pluckRequest = fetchCustomPluckPlayerRecords(playerId).then((data) => {
        pluckRecords.value = data;
    }).catch(() => {
        ElMessage.error({ message: '自定义密度纪录加载失败', offset: 68 });
    });
    const boards: SaoleiBoard[] = ['saolei', 'saolei_nf'];
    const saoleiRequests = boards.map(async (board) => {
        try {
            saoleiRecords.value[board] = await fetchSaoleiRecord(playerId, board);
        } catch {
            ElMessage.error({ message: '竞速纪录加载失败', offset: 68 });
        }
    });
    void Promise.all([pluckRequest, ...saoleiRequests]).finally(() => {
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
