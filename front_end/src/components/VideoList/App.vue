<template>
    <el-table :data="videos" size="small">
        <component
            :is="componentConfig[column].component" v-for="column in columns" :key="column"
            :sortable="componentConfig[column].sortable ? sortable : undefined"
            :stat="componentConfig[column].isStat ? column : undefined"
        />
    </el-table>
</template>

<script setup lang="ts">

import { VideoAbstract } from '@/utils/videoabstract';
import { ElTable } from 'element-plus';
import { defineAsyncComponent } from 'vue';

const ColumnLevel = defineAsyncComponent(() => import('./ColumnLevel.vue')); // eslint-disable-line @typescript-eslint/no-unused-vars
const ColumnState = defineAsyncComponent(() => import('./ColumnState.vue')); // eslint-disable-line @typescript-eslint/no-unused-vars
const ColumnUploadTime = defineAsyncComponent(() => import('./ColumnUploadTime.vue')); // eslint-disable-line @typescript-eslint/no-unused-vars

type columnChoices = 'level' | 'state' | 'upload_time';

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
    level: {
        component: 'ColumnLevel',
        sortable: false,
        isStat: false,
    },
    state: {
        component: 'ColumnState',
        sortable: false,
        isStat: false,
    },
    upload_time: {
        component: 'ColumnUploadTime',
        sortable: true,
        isStat: false,
    },
};

</script>
