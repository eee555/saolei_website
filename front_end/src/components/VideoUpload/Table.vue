<template>
    <PrDataTable
        v-if="data.length > 0"
        v-model:filters="filters"
        v-model:expanded-rows="expandedRows"
        filter-display="menu" :value="data" table-layout="auto" data-key="hash"
        :filter-button-props="{
            filter: {
                severity: 'secondary',
                text: true,
                rounded: false,
                size: 'small',
                style: { borderRadius: '0', padding: '0', width: '1rem' }
            }
        }"
        paginator :rows="25" row-hover
        paginator-template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown JumpToPageInput CurrentPageReport"
        :rows-per-page-options="[5, 10, 25, 50, 100]"
        @filter="onFilter"
    >
        <PrColumn expander />
        <PrColumn>
            <template #header>
                <ElCheckbox :model-value="!selectedNone && selectedAll" :indeterminate="!selectedAll && !selectedNone" @click="handleSelectAllClick" />
            </template>
            <template #body="{data}: {data: UploadEntry}">
                <ElCheckbox :model-value="selectedRows.includes(data)" @change="(value) => handleSelectOneChange(value, data)" />
            </template>
        </PrColumn>
        <PrColumn field="status" :header="t('common.prop.status')" :show-filter-match-modes="false" :show-filter-operator="false">
            <template #body="{data}: {data: UploadEntry}">
                {{ t(`local.${data.status}`) }}
            </template>
            <template #filter="{ filterModel, applyFilter }">
                <PrListbox v-model="filterModel.value" :options="[...UploadStatus]" @change="applyFilter()">
                    <template #option="slotProps">
                        {{ t(`local.${slotProps.option}`) }}
                    </template>
                </PrListbox>
            </template>
        </PrColumn>
        <PrColumn field="stat.end_time" :header="t('common.prop.end_time')" sortable>
            <template #body="{data}: {data: UploadEntry}">
                {{ data.stat ? toISODateTimeString(data.stat.end_time!) : '' }}
            </template>
        </PrColumn>
        <PrColumn field="stat.level" :header="t('common.prop.level')" :show-filter-match-modes="false" :show-filter-operator="false">
            <template #body="{data}: {data: UploadEntry}">
                {{ data.stat ? t(`common.level.${data.stat.level}`) : '' }}
            </template>
            <template #filter="{ filterModel, applyFilter }">
                <PrListbox v-model="filterModel.value" :options="[...MS_Levels]" @change="applyFilter()">
                    <template #option="slotProps">
                        {{ t(`common.level.${slotProps.option}`) }}
                    </template>
                </PrListbox>
            </template>
        </PrColumn>
        <PrColumn field="stat.timems" :header="t('common.prop.time')" sortable>
            <template #body="{data}: {data: UploadEntry}">
                {{ data.stat ? data.stat.displayStat('time') : '' }}
            </template>
        </PrColumn>
        <PrColumn field="stat.bv" :header="t('common.prop.bv')" sortable />
        <PrColumn field="stat.bvs" :header="t('common.prop.bvs')" sortable>
            <template #body="{data}: {data: UploadEntry}">
                {{ data.stat ? data.stat.displayStat('bvs') : '' }}
            </template>
        </PrColumn>
        <template #expansion="{data}: {data: UploadEntry}">
            <ElDescriptions>
                <ElDescriptionsItem :label="t('common.prop.fileName')" :span="3">
                    {{ data.file.name }}
                </ElDescriptionsItem>
                <template v-if="data.stat">
                    <ElDescriptionsItem :label="t('common.prop.cl')">
                        {{ data.stat.displayStat('cl') }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('common.prop.ce')" :span="2">
                        {{ data.stat.displayStat('ce') }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('common.prop.cl_s')">
                        {{ data.stat.displayStat('cls') }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('common.prop.ce_s')" :span="2">
                        {{ data.stat.displayStat('ces') }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('common.prop.ioe')">
                        {{ data.stat.displayStat('ioe') }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('common.prop.thrp')">
                        {{ data.stat.displayStat('thrp') }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('common.prop.corr')">
                        {{ data.stat.displayStat('corr') }}
                    </ElDescriptionsItem>
                </template>
            </ElDescriptions>
        </template>
    </PrDataTable>
</template>

<script setup lang="ts">
import { FilterMatchMode } from '@primevue/core/api';
import type { CheckboxValueType } from 'element-plus';
import { ElCheckbox, ElDescriptions, ElDescriptionsItem } from 'element-plus';
import PrColumn from 'primevue/column';
import type { DataTableFilterEvent } from 'primevue/datatable';
import PrDataTable from 'primevue/datatable';
import PrListbox from 'primevue/listbox';
import type { PropType } from 'vue';
import { computed, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import type { UploadEntry } from './utils';
import { UploadStatus } from './utils';

import { toISODateTimeString } from '@/utils/datetime';
import { MS_Levels } from '@/utils/ms_const';

defineProps({
    data: {
        type: Array as PropType<UploadEntry[]>,
        default: () => [],
    },
});

const selectedRows = defineModel<UploadEntry[]>(
    'selected-rows',
    { default: () => [] },
);

const filters = ref({
    status: { value: null, matchMode: FilterMatchMode.EQUALS },
    'stat.level': { value: null, matchMode: FilterMatchMode.EQUALS },
    // 'mode': { value: Object.values(MS_Mode), matchMode: FilterMatchMode.IN },
});

const filteredData = ref<UploadEntry[]>([]);
const expandedRows = ref<UploadEntry[]>([]);

const selectedAll = computed(() => selectedRows.value.length === filteredData.value.length);
const selectedNone = computed(() => selectedRows.value.length === 0);
function handleSelectAllClick() {
    if (!selectedNone.value) {
        selectedRows.value.length = 0;
    } else {
        selectedRows.value = [...filteredData.value];
    }
}

function onFilter(event: DataTableFilterEvent) {
    filteredData.value = event.filteredValue;
}
watch(filteredData, (newVal) => {
    selectedRows.value = selectedRows.value.filter((entry) => newVal.includes(entry));
});

function handleSelectOneChange(value: CheckboxValueType, entry: UploadEntry) {
    // eslint-disable-next-line @typescript-eslint/strict-boolean-expressions
    if (value) {
        selectedRows.value.push(entry);
    } else {
        const index = selectedRows.value.indexOf(entry);
        selectedRows.value.splice(index, 1);
    }
}

/* 本地化 Localization */
const i18nMessages = {
    'zh-cn': { local: {
        censorship: '标识未通过',
        collision: '录像已存在',
        custom: '暂不支持自定义级别',
        fail: '不通过',
        fileext: '无法识别的文件类型',
        filename: '文件名超过了100字节',
        filesize: '文件大小超过了5MB',
        identifier: '新标识',
        mode: '暂不支持此模式',
        needApprove: '需要人工审核',
        parse: '录像解析失败',
        pass: '通过',
        process: '上传中',
        success: '上传成功',
        upload: '上传失败',
    } },
    en: { local: {
        censorship: 'Identifier blocked',
        collision: 'Video already exists',
        custom: 'Custom level is currently not supported',
        fail: 'Fail',
        fileext: 'Invalid file extension',
        filename: 'File name exceeds 100 bytes',
        filesize: 'File size exceeds 5MB',
        identifier: 'New identifier',
        mode: 'Unsupported game mode',
        needApprove: 'Need manual approval',
        parse: 'Cannot parse the file',
        pass: 'Pass',
        process: 'Uploading',
        success: 'Success',
        upload: 'Upload fail',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>
