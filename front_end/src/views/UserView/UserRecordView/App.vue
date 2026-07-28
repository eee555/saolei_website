<template>
    <div class="user-record-view">
        <ElSkeleton v-show="loading" animated style="margin-top: 0px;" :rows="8" />
        <ClassicalCard :records="records" />
        <PLuckCard :records="pluckRecords" />
    </div>
</template>

<script lang="ts" setup>
import '@/styles/text.css';

import { ElMessage, ElSkeleton } from 'element-plus';
import { nextTick, ref } from 'vue';

import ClassicalCard from './ClassicalCard.vue';
import PLuckCard from './PLuckCard.vue';

import type {
    CustomPluckRecord,
    UserRecordLevel,
    UserRecordMode,
    UserRecordsResponse,
    UserRecordStat,
} from '@/services/msuserService';
import { fetchCustomPluckPlayerRecords, fetchUserRecords } from '@/services/msuserService';
import { store } from '@/store';
import type { Record as PlayerRecord } from '@/utils/common/structInterface';

const loading = ref(true);
const records = ref<PlayerRecord[][]>([]);
const pluckRecords = ref<CustomPluckRecord[]>([]);

// 此处和父组件配合，等一下从store里获取用户的id
void nextTick(() => {
    void fetchUserRecords(store.player.id).then((data) => {
        records.value = toPlayerRecords(data);
    }).catch(() => {
        ElMessage.error({ message: '不知哪里出现了问题', offset: 68 });
    }).finally(() => {
        loading.value = false;
    });

    void fetchCustomPluckPlayerRecords(store.player.id).then((data) => {
        pluckRecords.value = data;
    }).catch(() => {
        ElMessage.error({ message: '自定义密度纪录加载失败', offset: 68 });
    });
});

const recordModes: UserRecordMode[] = ['std', 'nf', 'ng', 'dg'];
const recordLevels: UserRecordLevel[] = ['b', 'i', 'e'];

function toPlayerRecords(data: UserRecordsResponse): PlayerRecord[][] {
    return recordModes.map((mode) => recordLevels.map((level) => toPlayerRecord(data, mode, level)));
}

function toPlayerRecord(data: UserRecordsResponse, mode: UserRecordMode, level: UserRecordLevel): PlayerRecord {
    return {
        timems: getStatValue(data, mode, level, 'timems'),
        bvs: getStatValue(data, mode, level, 'bvs'),
        stnb: getStatValue(data, mode, level, 'stnb'),
        ioe: getStatValue(data, mode, level, 'ioe'),
        path: getStatValue(data, mode, level, 'path'),
        timems_id: getStatId(data, mode, level, 'timems'),
        bvs_id: getStatId(data, mode, level, 'bvs'),
        stnb_id: getStatId(data, mode, level, 'stnb'),
        ioe_id: getStatId(data, mode, level, 'ioe'),
        path_id: getStatId(data, mode, level, 'path'),
    };
}

function getStatValue(
    data: UserRecordsResponse,
    mode: UserRecordMode,
    level: UserRecordLevel,
    stat: UserRecordStat,
): number {
    return data[`${level}_${stat}_${mode}`];
}

function getStatId(
    data: UserRecordsResponse,
    mode: UserRecordMode,
    level: UserRecordLevel,
    stat: UserRecordStat,
): number {
    return data[`${level}_${stat}_id_${mode}`] ?? 0;
}
</script>

<style scoped>
.user-record-view {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}
</style>
