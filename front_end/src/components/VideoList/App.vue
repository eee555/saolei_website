<template>
    <DataTable
        v-model:filters="filters" :value="videos" paginator-position="both" filter-display="menu" 
        style="min-width: 50em"
        :filter-button-props="{
            filter: {
                severity: 'secondary',
                text: true,
                rounded: false,
                size: 'small',
                style: { borderRadius: '0', padding: '0', width: '1rem' }
            }
        }"
        @row-click="(event: any) => preview(event.data.id)"
    >
        <component
            :is="componentConfig(column).component" v-for="column in columns" :key="column"
            :sortable="componentConfig(column).sortable ? sortable : undefined"
            :stat="componentConfig(column).isStat ? column : undefined"
        />
    </DataTable>
</template>

<script setup lang="ts">

import { FilterMatchMode } from '@primevue/core/api';
import { DataTable } from 'primevue';
import { defineAsyncComponent, ref } from 'vue';

import { preview } from '@/utils/common/PlayerDialog';
import { ColumnChoice, MS_Mode, MS_State } from '@/utils/ms_const';
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
    paginator: {
        type: Boolean,
        default: true,
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

const filters = ref({
    'state': { value: Object.values(MS_State), matchMode: FilterMatchMode.IN },
    'level': { value: null, matchMode: FilterMatchMode.EQUALS },
    'mode': { value: Object.values(MS_Mode), matchMode: FilterMatchMode.IN },
});

</script>

<style lang="less" scoped>
.p-datatable-popover-filter {
    display: none;
}

</style>
