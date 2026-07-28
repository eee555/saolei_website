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

import type { CustomPluckRecord } from '@/services/msuserService';
import { fetchCustomPluckPlayerRecords, fetchUserRecords } from '@/services/msuserService';
import { store } from '@/store';
import type { Record, RecordBIE } from '@/utils/common/structInterface';

const loading = ref(true);
const records = ref<Record[][]>([]);
const pluckRecords = ref<CustomPluckRecord[]>([]);

// 此处和父组件配合，等一下从store里获取用户的id
void nextTick(() => {
    void fetchUserRecords(store.player.id).then((result) => {
        if (result.type === 'error') {
            loading.value = false;
            ElMessage.error({ message: '不知哪里出现了问题', offset: 68 });
        } else {
            records.value = result.records.map(trans_record);
            loading.value = false;
        }
    });

    void fetchCustomPluckPlayerRecords(store.player.id).then((data) => {
        pluckRecords.value = data;
    }).catch(() => {
        ElMessage.error({ message: '自定义密度纪录加载失败', offset: 68 });
    });
});

// 把记录数据转一下嵌套的结构，做数据格式的适配
function trans_record(r: RecordBIE): Record[] {
    const record: Record[] = [];
    for (let i = 0; i < r.timems.length; i++) {
        record.push({
            timems: r.timems[i],
            bvs: r.bvs[i],
            stnb: r.stnb[i],
            ioe: r.ioe[i],
            path: r.path[i],
            timems_id: r.timems_id[i],
            bvs_id: r.bvs_id[i],
            stnb_id: r.stnb_id[i],
            ioe_id: r.ioe_id[i],
            path_id: r.path_id[i],
        });
    }
    return record;
}
</script>

<style scoped>
.user-record-view {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}
</style>
