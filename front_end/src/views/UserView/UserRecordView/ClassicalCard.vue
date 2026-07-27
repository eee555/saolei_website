<template>
    <BaseCardNormal v-for="(d, idx) in records" :key="idx">
        <table class="record-table" cellspacing="0" cellpadding="0">
            <thead>
                <tr>
                    <th class="text text-large" scope="col">
                        {{ t(`common.mode.${tableTitle[idx]}`) }}
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
</template>

<script lang="ts" setup>
import type { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import PreviewNumber from '@/components/PreviewNumber.vue';
import { ms_to_s } from '@/utils';
import type { Record } from '@/utils/common/structInterface';

defineProps({
    records: {
        type: Array as PropType<Record[][]>,
        required: true,
    },
});

const { t } = useI18n();

const tableTitle = ['std', 'nf', 'ng', 'dg'];
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
