<template>
    <div style="text-align: center;">
        <base-file-input :accept="'.avf,.evf,.rmv,.mvf'" :disabled="isUserAnonymous || isParsing || isUploading" :style="{ height: uploadQueue.length > 0 ? 'auto' : '300px' }" @add="handleFileChange">
            <FileInputContent :is-user-anonymous="isUserAnonymous" />
        </base-file-input>
    </div>
    <ToolBar v-if="uploadQueue.length > 0" v-model:stopping="pleaseStopUploading" :selected="selectedQueue.length" :total="uploadQueue.length" :processing="isWaiting" @upload="uploadSelected" @remove="removeSelected" />
    <Progress :parser-progress="parserProgress" :upload-progress="uploadProgress" />
    <Table v-if="uploadQueue.length > 0" v-model:selected-rows="selectedQueue" v-loading="isWaiting" :data="uploadQueue" />
</template>

<script setup lang="ts">
import { vLoading } from 'element-plus';
import { computed, PropType, ref } from 'vue';

import FileInputContent from './FileInputContent.vue';
import Progress from './Progress.vue';
import Table from './Table.vue';
import ToolBar from './ToolBar.vue';
import { fileCollide, UploadEntry, UploadStatus } from './utils';

import BaseFileInput from '@/components/common/BaseFileInput.vue';
import { local } from '@/store';
import { sleep } from '@/utils';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { AnyVideo, extract_stat, fileHash, load_video_file } from '@/utils/fileIO';
import { Dict2FormData } from '@/utils/forms';
import { getFileExtension } from '@/utils/strings';
import { VideoAbstract } from '@/utils/videoabstract';

const { proxy } = useCurrentInstance();

const props = defineProps({
    isUserAnonymous: { type: Boolean, default: true },
    identifiers: { type: Array as PropType<string[]>, default: () => [] },
});

const emit = defineEmits<{
    (e: 'onUpload', video: VideoAbstract): void;
}>();

const uploadQueue = ref<UploadEntry[]>([]);
const selectedQueue = ref<UploadEntry[]>([]);

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

async function handleFileChange(files: File[]) {
    if (!files) return;

    parserProgress.value.total = files.length;
    parserProgress.value.parsed = 0;

    const uploadQueueTemp: UploadEntry[] = [];

    for (let i = 0; i < files.length; i++) {
        const entry = await upload_prepare(files[i]);
        const exists = uploadQueue.value.some((e) => fileCollide(e, entry)) || uploadQueueTemp.some((e) => fileCollide(e, entry));
        if (!exists) {
            if (local.value.autoUploadAfterParse) {
                await forceUpload(entry);
            }
            if (entry.status !== 'success' || !local.value.autoRemoveAfterUpload) {
                uploadQueueTemp.push(entry);
            }
        }
        parserProgress.value.parsed += 1;
    }

    uploadQueue.value = [...uploadQueueTemp, ...uploadQueue.value];
}

const forceUpload = async (entry: UploadEntry) => {
    if (!['pass', 'identifier', 'needApprove'].includes(entry.status)) {
        return entry;
    }
    entry.status = 'process';
    if (entry.stat == null) {
        entry.status = 'upload';
        return entry;
    }
    await sleep(200);
    try {
        const response = await proxy.$axios.post('/common/uploadvideo/', Dict2FormData({
            file: entry.file,
        }));
        if (response.data.type === 'success') {
            entry.stat.id = response.data.data.id;
            entry.stat.state = response.data.data.state;
            entry.stat.upload_time = new Date(Date.now());
            emit('onUpload', entry.stat);
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
        console.error(_error);
        entry.status = 'upload';
    }
    return entry;
};

async function upload_prepare(file: File): Promise<UploadEntry> {
    const buffer = await file.arrayBuffer();
    const hash = await fileHash(buffer);
    let status: UploadStatus = 'pass';
    if (file.size > 5 * 1024 * 1024) status = 'filesize';
    else if (file.name.length >= 100) status = 'filename';
    else if (!['avf', 'evf', 'rmv', 'mvf'].includes(getFileExtension(file.name))) status = 'fileext';
    if (status !== 'pass') {
        return {
            hash: hash,
            file: file,
            status: status,
            stat: null,
        };
    }
    let video: AnyVideo;
    try {
        video = load_video_file(buffer, file.name);
    } catch (_e) {
        return {
            hash: hash,
            file: file,
            status: 'parse',
            stat: null,
        };
    }

    if (video.level == 6) status = 'custom';
    else if (video.is_valid() == 1) status = 'invalid';
    else if (video.is_valid() == 3) status = 'needApprove';
    else if (!props.identifiers.includes(video.player_identifier)) status = 'identifier';

    return {
        hash: hash,
        file: file,
        status: status,
        stat: extract_stat(video),
    };
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

        if (['pass', 'identifier', 'needApprove'].includes(entry.status)) {
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

    if (local.value.autoRemoveAfterUpload) {
        selectedQueue.value = selectedQueueTemp;
        uploadQueue.value = uploadQueueTemp;
    }
}

function removeSelected() {
    for (const entry of selectedQueue.value) {
        const index = uploadQueue.value.indexOf(entry);
        uploadQueue.value.splice(index, 1);
    }
    selectedQueue.value.length = 0;
}
</script>
