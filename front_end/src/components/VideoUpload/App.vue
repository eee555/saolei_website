<template>
    <div style="text-align: center;">
        <base-file-input :accept="'.avf,.evf,.rmv,.mvf'" :disabled="store.isUserAnonymous || isParsing || isUploading" :style="{ height: uploadQueue.length > 0 ? 'auto' : '300px' }" @add="handleFileChange">
            <FileInputContent :is-user-anonymous="isUserAnonymous" />
        </base-file-input>
    </div>
    <ToolBar v-if="uploadQueue.length > 0" v-model:stopping="pleaseStopUploading" :selected="selectedQueue.length" :total="uploadQueue.length" :processing="isWaiting" @upload="uploadSelected" @remove="removeSelected" />
    <Progress :parser-progress="parserProgress" :upload-progress="uploadProgress" />
    <Table v-if="uploadQueue.length > 0" v-model:selected-rows="selectedQueue" v-loading="isWaiting" :data="uploadQueue" />
</template>

<script setup lang="ts">
import { computed, PropType, ref } from 'vue';

import FileInputContent from './FileInputContent.vue';
import Progress from './Progress.vue';
import Table from './Table.vue';
import ToolBar from './ToolBar.vue';
import { simpleHash, UploadEntry } from './utils';

import BaseFileInput from '@/components/common/BaseFileInput.vue';
import { local, store } from '@/store';
import { sleep } from '@/utils';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { extract_stat, get_upload_status, load_video_file, upload_form } from '@/utils/fileIO';
import { Dict2FormData } from '@/utils/forms';

const { proxy } = useCurrentInstance();

defineProps({
    isUserAnonymous: { type: Boolean, default: true },
    identifiers: { type: Array as PropType<string[]>, default: () => [] },
});

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

function removeSelected() {
    for (const entry of selectedQueue.value) {
        const index = uploadQueue.value.indexOf(entry);
        uploadQueue.value.splice(index, 1);
    }
    selectedQueue.value.length = 0;
}
</script>
