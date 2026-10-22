<template>
    <p>CSV 表头：<code>{{ historyCsvHeaders(kind).join(',') }}</code>。成绩单位：毫秒。</p>
    <input type="file" accept=".csv" :disabled="busy" aria-label="成绩 CSV" data-cy="history-csv" @change="selectCsv">
    <BaseButton :disabled="!records.length || submitted" :loading="busy" data-cy="history-csv-submit" @click="submit">
        导入 {{ records.length }} 条成绩
    </BaseButton>
    <p v-if="error" role="alert" data-cy="history-csv-error">
        {{ error }}
    </p>
    <p data-cy="history-csv-progress">
        已确认成功 {{ confirmed }} / {{ records.length }}
    </p>
    <ul data-cy="history-csv-batches">
        <li v-for="message in messages" :key="message">
            {{ message }}
        </li>
    </ul>
</template>

<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue';
import type { PropType } from 'vue';

import { historyCsvHeaders, parseHistoryCsv, splitHistoryBatches } from './history';
import type { HistoryCsvRecord, HistoryKind } from './history';

import BaseButton from '@/components/common/BaseButton.vue';
import { importGSCHistoryScores } from '@/services/gscHistoryService';

const props = defineProps({ kind: { type: String as PropType<HistoryKind>, required: true } });
const emit = defineEmits<{ imported: [] }>();
const records = ref<HistoryCsvRecord[]>([]);
const confirmed = ref(0);
const submitted = ref(false);
const busy = ref(false);
const error = ref('');
const messages = ref<string[]>([]);
let stopped = false;
onBeforeUnmount(() => {
    stopped = true;
});

async function selectCsv(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    input.value = '';
    records.value = [];
    confirmed.value = 0;
    submitted.value = false;
    messages.value = [];
    error.value = '';
    if (!file) return;
    busy.value = true;
    try {
        records.value = parseHistoryCsv(await file.text(), props.kind);
    } catch (reason) {
        error.value = String(reason);
    } finally {
        busy.value = false;
    }
}

async function submit() {
    if (busy.value || submitted.value || !records.value.length) return;
    busy.value = true;
    submitted.value = true;
    const batches = splitHistoryBatches(records.value);
    try {
        for (const [index, batch] of batches.entries()) {
            if (stopped) break;
            const lines = batch.records.map((record) => record.sourceRow).join(', ');
            try {
                const count = await importGSCHistoryScores(props.kind, batch.order, batch.records.map((record) => record.data));
                confirmed.value += count;
                messages.value.push(`第 ${batch.order} 届，CSV 行 ${lines}：成功 ${count} 条`);
            } catch (reason) {
                error.value = `第 ${batch.order} 届，CSV 行 ${lines}：${String(reason)}。后续批次未提交。超时可能已写入，请先核对管理列表，再用仅含剩余记录的 CSV 重试。`;
                const remaining = batches.slice(index + 1).flatMap((pending) => pending.records.map((record) => record.sourceRow));
                if (remaining.length) messages.value.push(`未提交 CSV 行：${remaining.join(', ')}`);
                break;
            }
        }
    } finally {
        busy.value = false;
        emit('imported');
    }
}
</script>
