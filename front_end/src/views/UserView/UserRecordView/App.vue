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

import { store } from '@/store';
import type { Record, RecordBIE } from '@/utils/common/structInterface';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

interface PluckRecord {
    level: string;
    video_id: number;
    pluck: number;
}

const { proxy } = useCurrentInstance();

const loading = ref(true);
const records = ref<Record[][]>([]);
const pluckRecords = ref<PluckRecord[]>([]);

// 此处和父组件配合，等一下从store里获取用户的id
void nextTick(() => {
    void proxy.$axios.get('/msuser/records/', {
        params: {
            id: store.player.id,
        },
    }).then(function ({ data }) {
        if (data.status > 100) {
            loading.value = false;
            ElMessage.error({ message: '不知哪里出现了问题', offset: 68 });
        } else {
            records.value.push(trans_record(JSON.parse(data.std_record)));
            records.value.push(trans_record(JSON.parse(data.nf_record)));
            records.value.push(trans_record(JSON.parse(data.ng_record)));
            records.value.push(trans_record(JSON.parse(data.dg_record)));
            loading.value = false;
        }
    });

    void proxy.$axios.get<PluckRecord[]>('/api/customranking/pluck/player', {
        params: {
            player_id: store.player.id,
        },
    }).then(({ data }) => {
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
