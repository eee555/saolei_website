<template>
    <div class="auto-uploader">
        <div class="auto-uploader__controls">
            <div class="auto-uploader__control">
                <span class="auto-uploader__label">{{ t('local.folder') }}</span>
                <ElButton type="primary" size="small" :disabled="!canSelectDirectory || busy" :loading="selectingDirectory" @click="selectDirectory">
                    {{ directoryName || t('local.selectFolder') }}
                </ElButton>
                <ElButton v-if="running" size="small" @click="pauseWatching">
                    {{ t('local.stop') }}
                </ElButton>
                <ElButton v-else-if="emitter" size="small" :disabled="!canSelectDirectory || busy" @click="resumeWatching">
                    {{ t('local.resume') }}
                </ElButton>
            </div>
            <div class="auto-uploader__control">
                <span class="auto-uploader__label">{{ t('local.pollInterval') }}</span>
                <InputNumber v-model="pollIntervalSeconds" :min="1" :max="300" :disabled="running" />
            </div>
            <div class="auto-uploader__control">
                <span class="auto-uploader__label">{{ t('local.filter') }}</span>
                <slot name="filter" />
            </div>
        </div>

        <div class="auto-uploader__control text">
            <BaseTagSupport v-if="!directoryPickerSupported" :support="false">
                {{ t('local.unsupported') }}
            </BaseTagSupport>
            <BaseTagSupport v-if="!participantWindowOpen" :support="false">
                {{ t('local.outsideWindow') }}
            </BaseTagSupport>
        </div>
        <div class="auto-uploader__control text">
            <span v-if="running">
                {{ t('local.running', { folder: directoryName }) }}
            </span>
            <span v-else-if="directoryName !== ''">
                {{ t('local.stopped', { folder: directoryName }) }}
            </span>
            <span v-else>
                {{ t('local.idle') }}
            </span>
        </div>
        <div v-if="scannedCount > 0">
            <StackBar
                legend :data="[
                    { name: t('local.uploaded'), value: uploadedCount, color: 'var(--el-color-success)' },
                    { name: t('local.processing'), value: scannedCount - uploadedCount - skippedCount - failedCount, color: 'var(--el-color-warning)' },
                    { name: t('local.skipped'), value: skippedCount, color: 'var(--el-color-info)' },
                    { name: t('local.failed'), value: failedCount, color: 'var(--el-color-danger)' },
                ]"
            />
        </div>
        <ElDialog :model-value="scanDialog" :title="t('local.scanTitle')" :close-on-click-modal="false" :show-close="false" :close-on-press-escape="false" width="min(460px, 95vw)">
            <p>{{ t('local.existingFiles', { count: existingCount }) }}</p>
            <ElProgress v-if="fullScanning" :percentage="scanProgress" />
            <template #footer>
                <ElButton @click="cancelScan">
                    {{ t('local.cancel') }}
                </ElButton>
                <template v-if="!fullScanning">
                    <ElButton @click="beginWatching(false)">
                        {{ t('local.newOnly') }}
                    </ElButton>
                    <ElButton type="primary" @click="beginWatching(true)">
                        {{ t('local.scanAll') }}
                    </ElButton>
                </template>
            </template>
        </ElDialog>
    </div>
</template>

<script setup lang="ts">
import { ElButton, ElDialog, ElMessage, ElProgress } from 'element-plus';
import { computed, onBeforeUnmount, ref, shallowRef, watch } from 'vue';
import type { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import BaseTagSupport from '@/components/common/BaseTagSupport.vue';
import InputNumber from '@/components/common/InputNumber.vue';
import StackBar from '@/components/visualization/StackBar/App.vue';
import { uploadVideoFile } from '@/services/videoUploadService';
import type { VideoUploadResult } from '@/services/videoUploadService';
import { sleep } from '@/utils';
import { globalNow } from '@/utils/datetime';
import { createDirectoryNewFileEmitter, extract_stat, load_video_file } from '@/utils/fileIO';
import type { AnyVideo, DirectoryNewFileEmitter, DirectoryNewFileEvent } from '@/utils/fileIO';
import { TournamentParticipant } from '@/utils/tournaments';
import type { VideoAbstract } from '@/utils/videoabstract';

const props = defineProps({
    participant: { type: TournamentParticipant, required: true },
    filter: { type: Function as PropType<(video: AnyVideo, stat: VideoAbstract) => boolean>, required: true },
    enabled: { type: Boolean, default: true },
    disabled: { type: Boolean, default: false },
});

const emit = defineEmits<{ busy: [value: boolean] }>();

defineSlots<{
    filter?: () => unknown;
}>();

interface DirectoryPickerWindow extends Window {
    showDirectoryPicker?: (options?: { mode?: 'read' | 'readwrite' }) => Promise<FileSystemDirectoryHandle>;
}

interface AutoUploadVideo {
    filename: string;
    video: AnyVideo;
    stat: VideoAbstract;
}

const directoryName = ref('');
const emitter = shallowRef<DirectoryNewFileEmitter | null>(null);
const selectingDirectory = ref(false);
const pollIntervalSeconds = ref(3);
const processingQueue = ref(false);
const running = ref(false);
const scanDialog = ref(false);
const fullScanning = ref(false);
const existingCount = ref(0);
const scanCompleted = ref(0);
let generation = 0;
let disposed = false;
const uploadedCount = ref(0);
const failedCount = ref(0);
const skippedCount = ref(0);
const scannedCount = ref(0);

const directoryPickerSupported = computed(() => typeof window !== 'undefined' && typeof (window as DirectoryPickerWindow).showDirectoryPicker === 'function');
const participantWindowOpen = computed(() => {
    if (!props.participant.start_time || !props.participant.end_time) return false;
    return props.participant.start_time <= globalNow.value && globalNow.value < props.participant.end_time;
});
const busy = computed(() => running.value || processingQueue.value || selectingDirectory.value || scanDialog.value);
const canSelectDirectory = computed(() => directoryPickerSupported.value && participantWindowOpen.value && props.enabled && !props.disabled);
const scanProgress = computed(() => (existingCount.value === 0 ? 100 : Math.min(100, Math.floor(scanCompleted.value / existingCount.value * 100))));

async function selectDirectory() {
    const picker = (window as DirectoryPickerWindow).showDirectoryPicker;
    if (!picker || !canSelectDirectory.value || busy.value) return;
    const currentGeneration = ++generation;
    selectingDirectory.value = true;
    try {
        const selectedDirectory = await picker({ mode: 'read' });
        if (currentGeneration !== generation || !canSelectDirectory.value) return;
        directoryName.value = selectedDirectory.name;
        emitter.value?.stop();
        emitter.value = createDirectoryNewFileEmitter(selectedDirectory);
        emitter.value.onFile(processEvent);
        existingCount.value = 0;
        for await (const handle of selectedDirectory.values()) {
            if (currentGeneration !== generation) return;
            if (handle.kind === 'file') existingCount.value += 1;
        }
        scanDialog.value = true;
    } catch (error) {
        if (!(error instanceof DOMException && error.name === 'AbortError')) {
            console.error(error);
            ElMessage.error(t('local.selectFailed'));
        }
    } finally {
        selectingDirectory.value = false;
    }
}

async function beginWatching(scanExisting: boolean) {
    if (!canSelectDirectory.value || !emitter.value) return;
    const currentGeneration = generation;
    fullScanning.value = scanExisting;
    scanCompleted.value = 0;
    if (!scanExisting) scanDialog.value = false;
    running.value = true;
    try {
        await emitter.value.start(scanExisting, pollIntervalSeconds.value * 1000);
    } catch (error) {
        console.error(error);
        pauseWatching();
        ElMessage.error(t('local.selectFailed'));
    } finally {
        if (currentGeneration === generation) {
            fullScanning.value = false;
            scanDialog.value = false;
        }
    }
}

function pauseWatching() {
    emitter.value?.stop();
    running.value = false;
}

async function resumeWatching() {
    if (!canSelectDirectory.value || busy.value || !emitter.value) return;
    await beginWatching(true);
}

function cancelScan() {
    generation += 1;
    pauseWatching();
    emitter.value = null;
    directoryName.value = '';
    scanDialog.value = false;
    fullScanning.value = false;
}

async function processEvent(event: DirectoryNewFileEvent) {
    if (!running.value || !canSelectDirectory.value || disposed) return;
    const owner = props.participant;
    const currentGeneration = generation;
    processingQueue.value = true;
    try {
        await processFile(event.file, owner, currentGeneration);
        if (fullScanning.value) scanCompleted.value += 1;
        await sleep(200);
    } finally {
        processingQueue.value = false;
    }
}

async function processFile(file: File, owner: TournamentParticipant, currentGeneration: number) {
    scannedCount.value += 1;
    const video = await loadAutoUploadVideo(file);
    if (video === undefined) {
        skippedCount.value += 1;
        logFile('skip parse', file.name);
        return;
    }

    if (currentGeneration !== generation || disposed || !canSelectDirectory.value || owner !== props.participant || !props.filter(video.video, video.stat)) {
        skippedCount.value += 1;
        logUpload('skip filter', video);
        return;
    }

    logUpload('upload start', video);
    try {
        const result = await uploadVideoFile(file);
        if (result.type === 'success') {
            video.stat.id = result.id;
            video.stat.state = result.state;
            video.stat.upload_time = new Date();
            owner.addVideo(video.stat);
            uploadedCount.value += 1;
            logUpload('upload success', video, result);
        } else {
            failedCount.value += 1;
            logUpload('upload failed', video, result);
        }
    } catch (error) {
        console.error(error);
        failedCount.value += 1;
        logUpload('upload error', video);
    }
}

async function loadAutoUploadVideo(file: File): Promise<AutoUploadVideo | undefined> {
    try {
        const buffer = await file.arrayBuffer();
        const video = load_video_file(buffer, file.name);
        return {
            filename: file.name,
            video,
            stat: extract_stat(video),
        };
    } catch (error) {
        console.error(error);
        return undefined;
    }
}

function logFile(action: string, filename: string) {
    console.info('[AutoUploader]', action, { filename });
}

function logUpload(action: string, video: AutoUploadVideo, result?: VideoUploadResult) {
    console.info('[AutoUploader]', action, {
        filename: video.filename,
        level: video.stat.level,
        mode: video.stat.mode,
        timems: video.stat.timems,
        state: video.stat.state,
        result: result?.type,
        raceIdentifier: video.video.race_identifier,
    });
}

watch(canSelectDirectory, (canSelect) => {
    if (!canSelect) {
        if (scanDialog.value) cancelScan();
        else pauseWatching();
    }
}, { flush: 'sync' });
watch(() => props.participant.id, cancelScan, { flush: 'sync' });
watch(busy, (value) => {
    emit('busy', value);
}, { immediate: true, flush: 'sync' });

let badgeUpdate = Promise.resolve();
function updateBadge(active: boolean) {
    badgeUpdate = badgeUpdate.then(async () => {
        if (active && !disposed) await navigator.setAppBadge?.();
        else await navigator.clearAppBadge?.();
    }).catch(console.debug);
}
watch(processingQueue, updateBadge);
onBeforeUnmount(() => {
    disposed = true;
    cancelScan();
    updateBadge(false);
});

const i18nMessages = {
    'zh-cn': { local: {
        cancel: '取消',
        existingFiles: '文件夹中有 {count} 个文件',
        scanTitle: '扫描已有文件',
        scanAll: '扫描全部文件',
        newOnly: '仅监听新文件',
        resume: '继续',
        stopped: '已暂停监听 {folder}',
        failed: '失败',
        filter: '筛选级别',
        folder: '文件夹',
        idle: '未选择文件夹',
        outsideWindow: '不在参赛时间内',
        pollInterval: '轮询周期（秒）',
        processing: '处理中',
        running: '正在监听 {folder}',
        selectFailed: '无法读取该文件夹',
        selectFolder: '选择文件夹',
        skipped: '已跳过',
        stop: '暂停',
        uploaded: '已上传',
        unsupported: '当前浏览器不支持 showDirectoryPicker',
    } },
    en: { local: {
        cancel: 'Cancel',
        existingFiles: '{count} files in this folder',
        scanTitle: 'Scan existing files',
        scanAll: 'Scan all files',
        newOnly: 'Watch new files only',
        resume: 'Resume',
        stopped: 'Paused {folder}',
        failed: 'Failed',
        filter: 'Filter',
        folder: 'Folder',
        idle: 'No folder selected',
        outsideWindow: 'Outside session window',
        pollInterval: 'Poll interval (s)',
        processing: 'Processing',
        running: 'Watching {folder}',
        selectFailed: 'Cannot read this folder',
        selectFolder: 'Select folder',
        skipped: 'Skipped',
        stop: 'Pause',
        uploaded: 'Uploaded',
        unsupported: 'showDirectoryPicker is not supported by this browser',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>

<style scoped>
.auto-uploader {
    margin-bottom: 1rem;
}

.auto-uploader__controls {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem 1rem;
    align-items: center;
}

.auto-uploader__control {
    display: flex;
    gap: 0.5rem;
    align-items: center;
}

.auto-uploader__label {
    flex: none;
    color: var(--el-text-color-regular);
    font-size: 0.875rem;
}
</style>
