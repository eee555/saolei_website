<template>
    <div style="display: flex; flex-direction: column; gap: 1rem">
        <ElSkeleton v-show="loading" animated style="margin-top: 0px;" :rows="8" />
        <BaseCardNormal v-for="(d, idx) in records" :key="idx">
            <table class="record-table" cellspacing="0" cellpadding="0">
                <thead>
                    <tr>
                        <th class="text text-large" scope="col">
                            {{ t(`common.mode.${table_title[idx]}`) }}
                        </th>
                        <th v-for="column in recordColumns" :key="column.key" class="text text-info" scope="col">
                            {{ t(`common.prop.${column.label}`) }}
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(row, rowIndex) in d" :key="rowIndex">
                        <th class="text text-info" scope="row">
                            {{ levelLabel(rowIndex) }}
                        </th>
                        <td v-for="column in recordColumns" :key="column.key" class="text">
                            <PreviewNumber :id="row[column.idKey]" :text="column.format(row)" />
                        </td>
                    </tr>
                </tbody>
            </table>
        </BaseCardNormal>
    </div>
</template>

<script lang="ts" setup>
import '@/styles/text.css';

import { ElMessage, ElSkeleton } from 'element-plus';
import { nextTick, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import PreviewNumber from '@/components/PreviewNumber.vue';
import { store } from '@/store';
import { ms_to_s } from '@/utils';
import type { Record, RecordBIE } from '@/utils/common/structInterface';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

const { proxy } = useCurrentInstance();
const { t } = useI18n();

const loading = ref(true);

// 编辑前的
const userid = ref('');
const username = ref('');

// 个人纪录表格
const records = ref<Record[][]>([]);
const table_title = ['std', 'nf', 'ng', 'dg'];
const recordColumns = [
    { key: 'timems', idKey: 'timems_id', label: 'time', format: (row: Record) => ms_to_s(row.timems) },
    { key: 'bvs', idKey: 'bvs_id', label: 'bvs', format: (row: Record) => row.bvs.toFixed(3) },
    { key: 'stnb', idKey: 'stnb_id', label: 'stnb', format: (row: Record) => row.stnb.toFixed(3) },
    { key: 'ioe', idKey: 'ioe_id', label: 'ioe', format: (row: Record) => row.ioe.toFixed(3) },
    { key: 'path', idKey: 'path_id', label: 'path', format: (row: Record) => row.path.toFixed(3) },
] as const;

function levelLabel(index: number): string {
    return ['', t('common.level.b'), t('common.level.i'), t('common.level.e')][index + 1];
}

// 此处和父组件配合，等一下从store里获取用户的id
void nextTick(() => {
    // 把左侧的头像、姓名、个性签名、记录请求过来
    void proxy.$axios.get('/msuser/records/', {
        params: {
            id: store.player.id,
        },
    }).then(function ({ data }) {
        if (data.status > 100) {
            loading.value = false;
            ElMessage.error({ message: '不知哪里出现了问题', offset: 68 });
        } else {
            userid.value = data.id;
            username.value = data.realname;
            records.value.push(trans_record(JSON.parse(data.std_record)));
            records.value.push(trans_record(JSON.parse(data.nf_record)));
            records.value.push(trans_record(JSON.parse(data.ng_record)));
            records.value.push(trans_record(JSON.parse(data.dg_record)));
            loading.value = false;
        }
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
.record-table {
    width: 100%;
    table-layout: auto;
}

.record-table th,
.record-table td {
    box-sizing: border-box;
    border-bottom: 1px solid var(--el-table-border-color, var(--el-border-color-lighter));
    padding: 8px 12px;
    text-align: center;
    width: 16.66%;
}
</style>
