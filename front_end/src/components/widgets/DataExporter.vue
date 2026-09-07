<template>
    <ElButton :loading="isDownloading" @click="handleDownload">
        <slot />
    </ElButton>
    <ElSelect v-model="format" style="width: 5rem">
        <ElOption label="CSV" value="csv" />
        <ElOption label="JSON" value="json" />
    </ElSelect>
</template>

<script setup lang="ts" generic="TData extends object">
import { ElButton, ElOption, ElSelect } from 'element-plus';
import { jsonToCsv } from 'jtcsv/browser';
import { ref } from 'vue';
import type { PropType } from 'vue';

type MaybePromise<T> = T | Promise<T>;
type DataExportFormat = 'csv' | 'json';
type CsvRow = Record<string, unknown>;

const props = defineProps({
    fetchData: {
        type: Function as PropType<() => MaybePromise<TData[]>>,
        required: false,
        default: undefined,
    },
    lazy: {
        type: Boolean,
        default: false,
    },
    filename: {
        type: String,
        default: 'data',
    },
});

const data = defineModel<TData[]>({ default: () => [] });

const format = ref<DataExportFormat>('csv');
const isDownloading = ref(false);

async function handleDownload() {
    isDownloading.value = true;
    try {
        const exportData = await getExportData();
        if (exportData.length === 0) return;

        if (format.value === 'csv') {
            const csv = jsonToCsv(exportData as CsvRow[], { delimiter: ',' });
            if (csv === '') return;
            downloadFile(csv, 'text/csv;charset=utf-8', 'csv');
        } else {
            downloadFile(JSON.stringify(exportData, null, 2), 'application/json;charset=utf-8', 'json');
        }
    } finally {
        isDownloading.value = false;
    }
}

async function getExportData(): Promise<TData[]> {
    if (props.lazy && data.value.length > 0) return data.value;
    if (props.fetchData === undefined) return data.value;

    const fetchedData = await props.fetchData();
    data.value = fetchedData;
    return fetchedData;
}

function downloadFile(content: string, type: string, extension: DataExportFormat) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');

    a.href = url;
    a.download = getDownloadFilename(extension);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function getDownloadFilename(extension: DataExportFormat): string {
    const baseName = props.filename.trim() || 'data';
    return baseName.endsWith(`.${extension}`) ? baseName : `${baseName}.${extension}`;
}
</script>
