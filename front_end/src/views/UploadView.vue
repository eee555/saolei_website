<template>
    <div style="text-align: center;">
        <base-file-input :accept="'.avf,.evf,.rmv,.mvf'" :disabled="store.isUserAnonymous || isParsing || isUploading" :style="{ height: uploadQueue.length > 0 ? 'auto' : '300px' }" @add="handleFileChange">
            <span v-if="store.isUserAnonymous" class="text text-large">
                {{ t('common.msg.realNameRequired') }}
            </span>
            <div v-else>
                <div class="text text-large" style="padding: 0.1em; color: inherit;">
                    {{ t('local.dragOrClick') }}
                </div>
                <el-checkbox v-model="local.autoUploadAfterParse" :disabled="isParsing || isUploading" @click.stop>
                    {{ t('local.autoUploadAfterParse') }}
                </el-checkbox>
                <el-checkbox v-model="local.autoDeleteAfterUpload" :disabled="isParsing || isUploading" @click.stop>
                    {{ t('local.autoRemoveAfterUpload') }}
                </el-checkbox>
                <div class="text text-small" style="padding: 0.1em;">
                    {{ t('local.constraintNote') }}
                </div>
            </div>
        </base-file-input>
    </div>
    <div style="height: 1rem" />
    <div v-if="uploadQueue.length > 0">
        <span class="text">
            {{ t('local.selected', [selectedQueue.length, uploadQueue.length]) }}
        </span>
        &nbsp;
        <el-button :disabled="isWaiting || selectedNone" @click="uploadSelected">
            <base-icon-upload />&nbsp;{{ t('local.upload') }}
        </el-button>
        <el-button :disabled="isWaiting || selectedNone" @click="removeSelected">
            <base-icon-delete />&nbsp;{{ t('local.remove') }}
        </el-button>
    </div>
    <div v-if="isParsing" style="margin-top: 1em;">
        <span class="text">
            {{ t('local.parsing', [parserProgress.parsed, parserProgress.total]) }}
        </span>
        &nbsp;
        <StackBar
            :data="[
                { name: t('local.parsed'), value: parserProgress.parsed, color: '#409EFF' },
                { name: t('local.toParse'), value: parserProgress.total - parserProgress.parsed, color: '#C0C4CC' },
            ]"
        />
    </div>
    <div v-if="isUploading" style="margin-top: 1em;">
        <span class="text">
            {{ t('local.uploading', [uploadProgress.uploaded + uploadProgress.failed, uploadProgress.total]) }}
        </span>
        &nbsp;
        <el-button @click="pleaseStopUploading = true">
            {{ t('local.stopUpload') }}
        </el-button>
        <StackBar
            :data="[
                { name: t('local.uploaded'), value: uploadProgress.uploaded, color: '#67C23A' },
                { name: t('local.uploadFailed'), value: uploadProgress.failed, color: '#F56C6C' },
                { name: t('local.toUpload'), value: uploadProgress.total - uploadProgress.uploaded - uploadProgress.failed, color: '#C0C4CC' },
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
                {{ t(`local.status.${data.status}`) }}
            </template>
            <template #filter="{ filterModel, applyFilter }">
                <PrListbox v-model="filterModel.value" :options="[...UploadStatus]" @change="applyFilter()">
                    <template #option="slotProps">
                        {{ t(`local.status.${slotProps.option}`) }}
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
import { computed, PropType, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import { local, store } from '../store';

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

const UploadStatus = ['parse', 'pass', 'filename', 'fileext', 'custom', 'invalid', 'identifier', 'needApprove', 'censorship', 'collision', 'upload', 'process', 'success'] as const;
type UploadStatus = typeof UploadStatus[number];

interface UploadEntry {
    hash: string;
    filename: string;
    status: UploadStatus;
    form: UploadVideoForm | null; // for upload
    stat: VideoAbstract | null; // for display
}

defineProps({
    identifiers: { type: Array as PropType<string[]>, default: () => [] },
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
            const entry = await upload_prepare(files[i], hash);
            if (local.value.autoUploadAfterParse) {
                await forceUpload(entry);
            }
            if (entry.status !== 'success' || !local.value.autoDeleteAfterUpload) {
                uploadQueueTemp.push(entry);
            }
        }
        parserProgress.value.parsed += 1;
    }

    uploadQueue.value = [...uploadQueueTemp, ...uploadQueue.value];
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

    const selectedQueueTemp = [...selectedQueue.value];
    const uploadQueueTemp = [...uploadQueue.value];
    for (const entry of selectedQueue.value) {
        if (pleaseStopUploading.value) {
            uploadProgress.value.total = uploadProgress.value.uploaded + uploadProgress.value.failed;
            break;
        }

        if (['pass', 'identifier'].includes(entry.status)) {
            await forceUpload(entry);
            if (entry.status === 'success') {
                const selectedIndex = selectedQueueTemp.indexOf(entry);
                selectedQueueTemp.splice(selectedIndex, 1);
                const uploadIndex = uploadQueueTemp.indexOf(entry);
                uploadQueueTemp.splice(uploadIndex, 1);
                uploadProgress.value.uploaded += 1;
            } else {
                uploadProgress.value.failed += 1;
            }
        } else {
            uploadProgress.value.failed += 1;
        }
    }

    if (local.value.autoDeleteAfterUpload) {
        selectedQueue.value = selectedQueueTemp;
        uploadQueue.value = uploadQueueTemp;
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

/* 本地化 Localization */
const i18nMessages = {
    'zh-cn': { local: {
        dragOrClick: '将录像拉到此处或点击此处选择',
        autoUploadAfterParse: '解析完成自动上传',
        autoRemoveAfterUpload: '上传完成自动移除',
        constraintNote: '*单个文件大小不能超过5MB',
        selected: '已选中：{0} / {1}',
        upload: '上传',
        remove: '移除',
        parsing: '正在解析：{0} / {1}',
        parsed: '已解析',
        toParse: '待解析',
        uploading: '上传中：{0} / {1}',
        stopUpload: '停止上传',
        uploaded: '已上传',
        uploadFailed: '上传失败',
        toUpload: '待上传',
        status: {
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
        },
    } },
    'en': { local: {
        dragOrClick: 'Drag files here or click here to select',
        autoUploadAfterParse: 'Auto-upload after parsing',
        autoRemoveAfterUpload: 'Auto-remove after uploading',
        constraintNote: '*File size maximum is 5MB.',
        selected: 'Selected: {0} / {1}',
        upload: 'Upload',
        remove: 'Remove',
        parsing: 'Parsing files: {0} / {1}',
        parsed: 'Parsed',
        toParse: 'Not parsed',
        uploading: 'Uploading: {0} / {1}',
        stopUpload: 'Stop',
        uploaded: 'Uploaded',
        uploadFailed: 'Failed',
        toUpload: 'Queueing',
        status: {
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
        },
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>
