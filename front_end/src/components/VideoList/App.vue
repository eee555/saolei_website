<template>
    <el-table :data="videos" size="small" table-layout="auto" @row-click="(row: any) => preview(row.id)">
        <component
            :is="componentConfig[column].component" v-for="column in columns" :key="column"
            :sortable="componentConfig[column].sortable ? sortable : undefined"
            :stat="componentConfig[column].isStat ? column : undefined"
        />
    </el-table>
</template>

<script setup lang="ts">

import { preview } from '@/utils/common/PlayerDialog';
import { VideoAbstract } from '@/utils/videoabstract';
import { ElTable } from 'element-plus';
import { defineAsyncComponent } from 'vue';

const ColumnLevel = defineAsyncComponent(() => import('./ColumnLevel.vue'));
const ColumnStat = defineAsyncComponent(() => import('./ColumnStat.vue'));
const ColumnState = defineAsyncComponent(() => import('./ColumnState.vue'));
const ColumnSoftware = defineAsyncComponent(() => import('./ColumnSoftware.vue'));
const ColumnUploadTime = defineAsyncComponent(() => import('./ColumnUploadTime.vue'));

type columnChoices = 'bv' | 'bvs' | 'corr' | 'ioe' | 'level' | 'state' | 'software' | 'thrp' | 'time' | 'upload_time';

defineProps({
    videos: {
        type: Array<VideoAbstract>,
        default: () => [],
    },
    columns: {
        type: Array<columnChoices>,
        default: () => [],
    },
    sortable: {
        type: Boolean,
        default: false,
    },
});

const componentConfig = {
    bv: {
        component: ColumnStat,
        sortable: true,
        isStat: true,
    },
    bvs: {
        component: ColumnStat,
        sortable: true,
        isStat: true,
    },
    corr: {
        component: ColumnStat,
        sortable: true,
        isStat: true,
    },
    ioe: {
        component: ColumnStat,
        sortable: true,
        isStat: true,
    },
    level: {
        component: ColumnLevel,
        sortable: false,
        isStat: false,
    },
    software: {
        component: ColumnSoftware,
        sortable: false,
        isStat: false,
    },
    state: {
        component: ColumnState,
        sortable: false,
        isStat: false,
    },
    thrp: {
        component: ColumnStat,
        sortable: true,
        isStat: true,
    },
    time: {
        component: ColumnStat,
        sortable: true,
        isStat: true,
    },
    upload_time: {
        component: ColumnUploadTime,
        sortable: true,
        isStat: false,
    },
};

</script>
