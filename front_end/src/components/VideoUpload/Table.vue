<template>
    <pr-data-table
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
        <pr-column expander />
        <pr-column>
            <template #header>
                <el-checkbox :model-value="!selectedNone && selectedAll" :indeterminate="!selectedAll && !selectedNone" @click="handleSelectAllClick" />
            </template>
            <template #body="{data}: {data: UploadEntry}">
                <el-checkbox :model-value="selectedRows.includes(data)" @change="(value) => handleSelectOneChange(value, data)" />
            </template>
        </pr-column>
        <pr-column field="status" :header="t('common.prop.status')" :show-filter-match-modes="false" :show-filter-operator="false">
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
        </pr-column>
        <pr-column field="stat.end_time" :header="t('common.prop.end_time')" sortable>
            <template #body="{data}: {data: UploadEntry}">
                {{ data.stat ? toISODateTimeString(data.stat.end_time!) : '' }}
            </template>
        </pr-column>
        <pr-column field="stat.level" :header="t('common.prop.level')" :show-filter-match-modes="false" :show-filter-operator="false">
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
        </pr-column>
        <pr-column field="stat.timems" :header="t('common.prop.time')" sortable>
            <template #body="{data}: {data: UploadEntry}">
                {{ data.stat ? data.stat.displayStat('time') : '' }}
            </template>
        </pr-column>
        <pr-column field="stat.bv" :header="t('common.prop.bv')" sortable />
        <pr-column field="stat.bvs" :header="t('common.prop.bvs')" sortable>
            <template #body="{data}: {data: UploadEntry}">
                {{ data.stat ? data.stat.displayStat('bvs') : '' }}
            </template>
        </pr-column>
        <template #expansion="{data}: {data: UploadEntry}">
            <el-descriptions>
                <el-descriptions-item :label="t('common.prop.fileName')" :span="3">
                    {{ data.filename }}
                </el-descriptions-item>
                <template v-if="data.stat">
                    <el-descriptions-item :label="t('common.prop.cl')">
                        {{ data.stat.displayStat('cl') }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('common.prop.ce')" :span="2">
                        {{ data.stat.displayStat('ce') }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('common.prop.cl_s')">
                        {{ data.stat.displayStat('cls') }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('common.prop.ce_s')" :span="2">
                        {{ data.stat.displayStat('ces') }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('common.prop.ioe')">
                        {{ data.stat.displayStat('ioe') }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('common.prop.thrp')">
                        {{ data.stat.displayStat('thrp') }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('common.prop.corr')">
                        {{ data.stat.displayStat('corr') }}
                    </el-descriptions-item>
                </template>
            </el-descriptions>
        </template>
    </pr-data-table>
</template>

<script setup lang="ts">
import { FilterMatchMode } from '@primevue/core/api';
import { CheckboxValueType, ElCheckbox, ElDescriptions, ElDescriptionsItem } from 'element-plus';
import PrColumn from 'primevue/column';
import PrDataTable, { DataTableFilterEvent } from 'primevue/datatable';
import PrListbox from 'primevue/listbox';
import { computed, PropType, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import { UploadEntry, UploadStatus } from './utils';

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
    'status': { value: null, matchMode: FilterMatchMode.EQUALS },
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
        collision: '录像已存在',
        custom: '暂不支持自定义级别',
        identifier: '新标识',
        fail: '不通过',
        fileext: '无法识别的文件类型',
        filename: '文件名超过了100字节',
        filesize: '文件大小超过了5MB',
        mode: '暂不支持此模式',
        needApprove: '需要人工审核',
        parse: '录像解析失败',
        pass: '通过',
        process: '上传中',
        success: '上传成功',
        upload: '上传失败',
    } },
    'en': { local: {
        collision: 'Video already exist',
        custom: 'Custom level is currently not supported',
        identifier: 'New identifier',
        fail: 'Fail',
        fileext: 'Invalid file extension',
        filename: 'File name exceeds 100 bytes',
        filesize: 'File size exceeds 5MB',
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
