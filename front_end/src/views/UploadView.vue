<template>
    <div style="text-align: center;">
        <base-file-input :accept="'.avf,.evf,.rmv,.mvf'" :disabled="store.isUserAnonymous || isParsing || isUploading" :style="{ height: uploadQueue.length > 0 ? '50px' : '300px' }" @add="handleFileChange">
            <span v-if="store.isUserAnonymous" class="text-large">
                {{ t('common.msg.realNameRequired') }}
            </span>
            <div v-else>
                <div class="text-large" style="padding: 0.1em">
                    {{ t('profile.upload.dragOrClick') }}
                </div>
                <div class="text-small" style="padding: 0.1em">
                    {{ t('profile.upload.constraintNote') }}
                </div>
            </div>
        </base-file-input>
    </div>
    <div style="height: 1rem" />
    <div v-if="uploadQueue.length > 0">
        <span class="text-normal">
            {{ t('profile.upload.selected', [selectedQueue.length, uploadQueue.length]) }}
        </span>
        &nbsp;
        <el-button :disabled="isWaiting || selectedNone" @click="uploadSelected">
            <base-icon-upload />&nbsp;{{ t('profile.upload.upload') }}
        </el-button>
        <el-button :disabled="isWaiting || selectedNone" @click="removeSelected">
            <base-icon-delete />&nbsp;{{ t('profile.upload.delete') }}
        </el-button>
    </div>
    <div v-if="isParsing" style="margin-top: 1em;">
        <span class="text-normal">
            {{ t('profile.upload.parsing', [parserProgress.parsed, parserProgress.total]) }}
        </span>
        &nbsp;
        <StackBar
            :data="[
                { name: t('profile.upload.parsed'), value: parserProgress.parsed, color: '#409EFF' },
                { name: t('profile.upload.toParse'), value: parserProgress.total - parserProgress.parsed, color: '#C0C4CC' },
            ]"
        />
    </div>
    <div v-if="isUploading" style="margin-top: 1em;">
        <span class="text-normal">
            {{ t('profile.upload.uploading', [uploadProgress.uploaded + uploadProgress.failed, uploadProgress.total]) }}
        </span>
        &nbsp;
        <el-button @click="pleaseStopUploading = true">
            {{ t('profile.upload.stopUpload') }}
        </el-button>
        <StackBar
            :data="[
                { name: t('profile.upload.uploaded'), value: uploadProgress.uploaded, color: '#67C23A' },
                { name: t('profile.upload.uploadFailed'), value: uploadProgress.failed, color: '#F56C6C' },
                { name: t('profile.upload.toUpload'), value: uploadProgress.total - uploadProgress.uploaded - uploadProgress.failed, color: '#C0C4CC' },
            ]"
        />
    </div>
    <pr-data-table
        v-if="uploadQueue.length > 0"
        v-model:filters="filters"
        v-model:expanded-rows="expandedRows"
        v-loading="isWaiting" filter-display="menu" :value="uploadQueue" table-layout="auto" data-key="hash"
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
                <el-checkbox :model-value="selectedQueue.includes(data)" @change="(value) => handleSelectOneChange(value, data)" />
            </template>
        </pr-column>
        <pr-column field="status" :header="t('common.prop.status')" :show-filter-match-modes="false" :show-filter-operator="false">
            <template #body="{data}: {data: UploadEntry}">
                {{ t(`profile.upload.error.${data.status}`) }}
            </template>
            <template #filter="{ filterModel, applyFilter }">
                <PrListbox v-model="filterModel.value" :options="[...UploadStatus]" @change="applyFilter()">
                    <template #option="slotProps">
                        {{ t(`profile.upload.error.${slotProps.option}`) }}
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

<script lang="ts" setup>
import '@/styles/text.css';

import { FilterMatchMode } from '@primevue/core/api';
import { CheckboxValueType, ElButton, ElCheckbox, ElDescriptions, ElDescriptionsItem, vLoading } from 'element-plus';
import PrColumn from 'primevue/column';
import PrDataTable, { DataTableFilterEvent } from 'primevue/datatable';
import PrListbox from 'primevue/listbox';
import { computed, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import { store } from '../store';

import BaseFileInput from '@/components/common/BaseFileInput.vue';
import { BaseIconDelete, BaseIconUpload } from '@/components/common/icon';
import StackBar from '@/components/visualization/StackBar/App.vue';
import { sleep } from '@/utils';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { toISODateTimeString } from '@/utils/datetime';
import { extract_stat, get_upload_status, load_video_file, upload_form, UploadVideoForm } from '@/utils/fileIO';
import { Dict2FormData } from '@/utils/forms';
import { MS_Levels } from '@/utils/ms_const';
import { VideoAbstract } from '@/utils/videoabstract';

const { proxy } = useCurrentInstance();
const { t } = useI18n();

const UploadStatus = ['parse', 'pass', 'filename', 'fileext', 'custom', 'invalid', 'identifier', 'needApprove', 'censorship', 'collision', 'upload', 'process', 'success'] as const;
type UploadStatus = 'parse' | 'pass' | 'filename' | 'fileext' | 'custom' | 'invalid' | 'identifier' | 'needApprove' | 'censorship' | 'collision' | 'upload' | 'process' | 'success';

interface UploadEntry {
    hash: string;
    filename: string;
    status: UploadStatus;
    form: UploadVideoForm | null; // for upload
    stat: VideoAbstract | null; // for display
}

defineProps({
    identifiers: { type: Array, default: () => [] },
});

const filters = ref({
    'status': { value: null, matchMode: FilterMatchMode.EQUALS },
    'stat.level': { value: null, matchMode: FilterMatchMode.EQUALS },
    // 'mode': { value: Object.values(MS_Mode), matchMode: FilterMatchMode.IN },
});

const uploadQueue = ref<UploadEntry[]>([]);
const selectedQueue = ref<UploadEntry[]>([]);
const filteredQueue = ref<UploadEntry[]>([]);
const expandedRows = ref<UploadEntry[]>([]);

const selectedAll = computed(() => selectedQueue.value.length === filteredQueue.value.length);
const selectedNone = computed(() => selectedQueue.value.length === 0);
function handleSelectAllClick() {
    if (!selectedNone.value) {
        selectedQueue.value.length = 0;
    } else {
        selectedQueue.value = [...filteredQueue.value];
    }
}

const parserProgress = ref({
    total: 0,
    parsed: 0,
});
const isParsing = computed(() => parserProgress.value.total != parserProgress.value.parsed);

const uploadProgress = ref({
    total: 0,
    uploaded: 0,
    failed: 0,
});
const isUploading = computed(() => uploadProgress.value.uploaded + uploadProgress.value.failed != uploadProgress.value.total);

const isWaiting = computed(() => isParsing.value || isUploading.value);

const pleaseStopUploading = ref(false);

function simpleHash(file: File) {
    return `${file.name}_${file.size}_${file.lastModified}`;
}

async function handleFileChange(files: File[]) {
    if (!files) return;
    parserProgress.value.total = files.length;
    parserProgress.value.parsed = 0;
    const uploadQueueTemp: UploadEntry[] = [];
    for (let i = 0; i < files.length; i++) {
        const hash = simpleHash(files[i]);
        const exists = uploadQueue.value.some((entry) => entry.hash === hash) || uploadQueueTemp.some((entry) => entry.hash === hash);
        if (!exists) {
            uploadQueueTemp.push(await upload_prepare(files[i], hash));
        }
        parserProgress.value.parsed += 1;
    }
    uploadQueue.value = [...uploadQueue.value, ...uploadQueueTemp];
}

function onFilter(event: DataTableFilterEvent) {
    filteredQueue.value = event.filteredValue;
}
watch(filteredQueue, (newVal) => {
    selectedQueue.value = selectedQueue.value.filter((entry) => newVal.includes(entry));
});

function handleSelectOneChange(value: CheckboxValueType, entry: UploadEntry) {
    if (value) {
        selectedQueue.value.push(entry);
    } else {
        const index = selectedQueue.value.indexOf(entry);
        selectedQueue.value.splice(index, 1);
    }
}

function removeSelected() {
    // uploadQueue.value.splice(0, uploadQueue.value.length);
    for (const entry of selectedQueue.value) {
        const index = uploadQueue.value.indexOf(entry);
        uploadQueue.value.splice(index, 1);
    }
    selectedQueue.value.length = 0;
}

async function uploadSelected() {
    uploadProgress.value.total = selectedQueue.value.length;
    uploadProgress.value.uploaded = 0;
    uploadProgress.value.failed = 0;
    pleaseStopUploading.value = false;

    for (const entry of selectedQueue.value) {
        if (pleaseStopUploading.value) {
            uploadProgress.value.total = uploadProgress.value.uploaded + uploadProgress.value.failed;
            return;
        }

        if (['pass', 'identifier'].includes(entry.status)) {
            await forceUpload(entry);
            if (entry.status === 'success') {
                uploadProgress.value.uploaded += 1;
            } else {
                uploadProgress.value.failed += 1;
            }
        }
    }
}

// 上传问题不大的录像
const forceUpload = async (entry: UploadEntry) => {
    if (entry.status != 'pass' && entry.status != 'identifier') {
        return entry;
    }
    entry.status = 'process';
    if (entry.stat == null) {
        entry.status = 'upload';
        return entry;
    }
    await sleep(200);
    try {
        const response = await proxy.$axios.post('/common/uploadvideo/', Dict2FormData(entry.form!));
        if (response.data.type === 'success') {
            entry.stat.id = response.data.data.id;
            entry.stat.state = response.data.data.state;
            store.user.videos.push(entry.stat!);
            if (store.user.id === store.player.id) {
                store.player.videos.push(entry.stat!);
            }
            entry.status = 'success';
            return entry;
        } else if (response.data.type === 'error' && response.data.object === 'file') {
            entry.status = 'collision';
        } else if (response.data.type === 'error' && response.data.object === 'identifier') {
            entry.status = 'censorship';
        } else {
            // 正常使用不会到这里
            entry.status = 'upload';
        }
    } catch (_error) {
        entry.status = 'upload';
    }
    return entry;
};

async function upload_prepare(file: File, hash: string): Promise<UploadEntry> {
    const file_u8 = new Uint8Array(await file.arrayBuffer());
    try {
        const video = load_video_file(file_u8, file.name);
        return {
            hash: hash,
            filename: file.name,
            status: get_upload_status(file, video, store.user.identifiers),
            stat: extract_stat(video),
            form: upload_form(file, video),
        };
    } catch (_e) {
        return {
            hash: hash,
            filename: file.name,
            status: 'parse',
            stat: null,
            form: null,
        };
    }
}

</script>
