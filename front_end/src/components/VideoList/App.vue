<template>
    <el-table :data="videos" size="small" table-layout="auto" @row-click="(row: any) => preview(row.id)">
        <component
            :is="componentConfig(column).component" v-for="column in columns" :key="column"
            :sortable="componentConfig(column).sortable ? sortable : undefined"
            :stat="componentConfig(column).isStat ? column : undefined"
        />
    </el-table>
</template>

<script setup lang="ts">

import { ElTable } from 'element-plus';
import { defineAsyncComponent } from 'vue';

import { preview } from '@/utils/common/PlayerDialog';
import { ColumnChoice } from '@/utils/ms_const';
import { VideoAbstract } from '@/utils/videoabstract';

const ColumnEndTime = defineAsyncComponent(() => import('./ColumnEndTime.vue'));
const ColumnFileSize = defineAsyncComponent(() => import('./ColumnFileSize.vue'));
const ColumnLevel = defineAsyncComponent(() => import('./ColumnLevel.vue'));
const ColumnMode = defineAsyncComponent(() => import('./ColumnMode.vue'));
const ColumnPlayerName = defineAsyncComponent(() => import('./ColumnPlayerName.vue'));
const ColumnStat = defineAsyncComponent(() => import('./ColumnStat.vue'));
const ColumnState = defineAsyncComponent(() => import('./ColumnState.vue'));
const ColumnSoftware = defineAsyncComponent(() => import('./ColumnSoftware.vue'));
const ColumnUploadTime = defineAsyncComponent(() => import('./ColumnUploadTime.vue'));

defineProps({
    videos: {
        type: Array<VideoAbstract>,
        default: () => [],
    },
    columns: {
        type: Array<ColumnChoice>,
        default: () => [],
    },
    sortable: {
        type: Boolean,
        default: false,
    },
});

function componentConfig(choice: ColumnChoice) {
    switch (choice) {
        case 'level': return {
            component: ColumnLevel,
            sortable: false,
            isStat: false,
        };
        case 'mode': return {
            component: ColumnMode,
            sortable: false,
            isStat: false,
        };
        case 'player': return {
            component: ColumnPlayerName,
            sortable: false,
            isStat: false,
        };
        case 'software': return {
            component: ColumnSoftware,
            sortable: false,
            isStat: false,
        };
        case 'state': return {
            component: ColumnState,
            sortable: false,
            isStat: false,
        };
        case 'upload_time': return {
            component: ColumnUploadTime,
            sortable: true,
            isStat: false,
        };
        case 'end_time': return {
            component: ColumnEndTime,
            sortable: true,
            isStat: false,
        };
        case 'file_size': return {
            component: ColumnFileSize,
            sortable: true,
            isStat: false,
        };
        default: return {
            component: ColumnStat,
            sortable: true,
            isStat: true,
        };
    }
}

</script>
