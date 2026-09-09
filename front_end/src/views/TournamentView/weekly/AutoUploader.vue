<template>
    <div class="auto-uploader">
        <div class="auto-uploader__controls">
            <div class="auto-uploader__control">
                <span class="auto-uploader__label">{{ t('local.folder') }}</span>
                <ElButton type="primary" :disabled="!canSelectDirectory" :loading="selectingDirectory" @click="selectDirectory">
                    {{ directoryName || t('local.selectFolder') }}
                </ElButton>
                <ElButton v-if="running" :disabled="processingQueue" @click="stopWatching">
                    {{ t('local.stop') }}
                </ElButton>
            </div>
            <div class="auto-uploader__control">
                <span class="auto-uploader__label">{{ t('local.pollInterval') }}</span>
                <InputNumber v-model="pollIntervalSeconds" :min="1" :max="300" :disabled="running" />
            </div>
            <div class="auto-uploader__control">
                <span class="auto-uploader__label">{{ t('local.filter') }}</span>
                <ElSelect v-model="filterLevel" size="small" style="width: 180px">
                    <ElOption :label="t('local.filterTournament')" value="tournament" />
                    <ElOption :label="t('local.filterSupported')" value="supported" />
                    <ElOption :label="t('local.filterScoreRefreshing')" value="scoreRefreshing" />
                </ElSelect>
            </div>
        </div>

        <div class="auto-uploader__status text">
            <BaseTagSupport v-if="!directoryPickerSupported" :support="false">
                {{ t('local.unsupported') }}
            </BaseTagSupport>
            <BaseTagSupport v-if="!participantWindowOpen" :support="false">
                {{ t('local.outsideWindow') }}
            </BaseTagSupport>
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
                    { name: t('local.uploaded'), value: uploadedCount, color: 'red' },
                    { name: t('local.processing'), value: scannedCount - uploadedCount - skippedCount - failedCount, color: 'orange' },
                    { name: t('local.skipped'), value: skippedCount, color: 'green' },
                    { name: t('local.failed'), value: failedCount, color: 'blue' },
                ]"
            />
        </div>
    </div>
</template>

<script setup lang="ts">
import { ElButton, ElMessage, ElOption, ElSelect } from 'element-plus';
import { computed, onBeforeUnmount, ref, watch } from 'vue';
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
import type { VideoAbstract } from '@/utils/videoabstract';
import { isWeeklyClassicScoreMode, WeeklyParticipant, WeeklyTournamentFormat } from '@/utils/weekly';

const props = defineProps({
    format: { type: String as PropType<WeeklyTournamentFormat>, required: true },
    participant: { type: WeeklyParticipant, required: true },
});
const WeeklyAutoUploadFilter = {
    Tournament: 'tournament',
    Supported: 'supported',
    ScoreRefreshing: 'scoreRefreshing',
} as const;
type WeeklyAutoUploadFilter = typeof WeeklyAutoUploadFilter[keyof typeof WeeklyAutoUploadFilter];

interface DirectoryPickerWindow extends Window {
    showDirectoryPicker?: (options?: { mode?: 'read' | 'readwrite' }) => Promise<FileSystemDirectoryHandle>;
}

interface AutoUploadVideo {
    filename: string;
    video: AnyVideo;
    stat: VideoAbstract;
}

const directory = ref<FileSystemDirectoryHandle | null>(null);
const directoryName = ref('');
const emitter = ref<DirectoryNewFileEmitter | null>(null);
const selectingDirectory = ref(false);
const filterLevel = ref<WeeklyAutoUploadFilter>(WeeklyAutoUploadFilter.Supported);
const pollIntervalSeconds = ref(3);
const pendingFiles: File[] = [];
const processingQueue = ref(false);
const uploadedCount = ref(0);
const failedCount = ref(0);
const skippedCount = ref(0);
const scannedCount = ref(0);

const directoryPickerSupported = computed(() => typeof window !== 'undefined' && typeof (window as DirectoryPickerWindow).showDirectoryPicker === 'function');
const participantWindowOpen = computed(() => {
    if (!props.participant.start_time || !props.participant.end_time) return false;
    return props.participant.start_time <= globalNow.value && globalNow.value < props.participant.end_time;
});
const running = computed(() => emitter.value?.running ?? false);
const canSelectDirectory = computed(() => directoryPickerSupported.value && participantWindowOpen.value);

async function selectDirectory() {
    const picker = (window as DirectoryPickerWindow).showDirectoryPicker;
    if (!picker || !canSelectDirectory.value) return;
    selectingDirectory.value = true;
    try {
        const selectedDirectory = await picker({ mode: 'read' });
        await startWatching(selectedDirectory);
    } catch (error) {
        if (!(error instanceof DOMException && error.name === 'AbortError')) {
            console.error(error);
            ElMessage.error(t('local.selectFailed'));
        }
    }
    selectingDirectory.value = false;
}

async function startWatching(selectedDirectory: FileSystemDirectoryHandle) {
    stopWatching();
    directory.value = selectedDirectory;
    directoryName.value = selectedDirectory.name;
    const newEmitter = createDirectoryNewFileEmitter(selectedDirectory, {
        pollIntervalMs: pollIntervalSeconds.value * 1000,
    });
    newEmitter.onFile(enqueueFile);
    await newEmitter.start();
    emitter.value = newEmitter;
}

function stopWatching() {
    emitter.value?.stop();
    emitter.value = null;
}

function enqueueFile(event: DirectoryNewFileEvent) {
    pendingFiles.push(event.file);
    void drainQueue();
}

async function drainQueue() {
    if (processingQueue.value) return;
    processingQueue.value = true;
    while (pendingFiles.length > 0) {
        const file = pendingFiles.shift();
        if (file) {
            await processFile(file);
            await sleep(200);
        }
    }
    processingQueue.value = false;
}

async function processFile(file: File) {
    scannedCount.value += 1;
    const video = await loadAutoUploadVideo(file);
    if (video === undefined) {
        skippedCount.value += 1;
        logFile('skip parse', file.name);
        return;
    }

    if (!matchesFilter(video)) {
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
            props.participant.addVideo(video.stat);
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

function matchesFilter(video: AutoUploadVideo): boolean {
    if (!isTournamentVideo(video)) return false;
    if (filterLevel.value === WeeklyAutoUploadFilter.Tournament) return true;
    if (!isWeeklySupportedVideo(video)) return false;
    if (filterLevel.value === WeeklyAutoUploadFilter.Supported) return true;
    return canRefreshWeeklyScore(video);
}

function isTournamentVideo(video: AutoUploadVideo): boolean {
    return video.video.race_identifier.split(',').map((identifier) => identifier.trim()).includes(props.participant.token);
}

function isWeeklySupportedVideo(video: AutoUploadVideo | VideoAbstract): boolean {
    const stat = getStat(video);
    if (props.format !== WeeklyTournamentFormat.Classic) return false;
    return (stat.level === 'i' || stat.level === 'e') && isWeeklyClassicScoreMode(stat.mode);
}

function canRefreshWeeklyScore(video: AutoUploadVideo): boolean {
    if (!isWeeklySupportedVideo(video)) return false;
    const { level } = video.stat;
    if (level !== 'i' && level !== 'e') return false;
    const currentBoundary = level === 'i'
        ? props.participant.classic_it[4][1]
        : props.participant.classic_et[1][1];
    return video.stat.timems < currentBoundary;
}

function getStat(video: AutoUploadVideo | VideoAbstract): VideoAbstract {
    return 'stat' in video ? video.stat : video;
}

function logFile(action: string, filename: string) {
    console.info('[WeeklyAutoUploader]', action, { filename });
}

function logUpload(action: string, video: AutoUploadVideo, result?: VideoUploadResult) {
    console.info('[WeeklyAutoUploader]', action, {
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
    if (!canSelect) stopWatching();
});

onBeforeUnmount(stopWatching);

const i18nMessages = {
    'zh-cn': { local: {
        failed: '失败',
        filter: '筛选级别',
        filterScoreRefreshing: '刷新成绩的录像',
        filterSupported: '比赛支持的录像',
        filterTournament: '比赛录像',
        folder: '文件夹',
        idle: '未选择文件夹',
        outsideWindow: '不在参赛时间内',
        pollInterval: '轮询周期（秒）',
        processing: '处理中',
        running: '正在监听 {folder}',
        selectFailed: '无法读取该文件夹',
        selectFolder: '选择文件夹',
        skipped: '已跳过',
        stop: '停止',
        uploaded: '已上传',
        unsupported: '当前浏览器不支持目录监听',
    } },
    en: { local: {
        failed: 'Failed',
        filter: 'Filter',
        filterScoreRefreshing: 'Score-improving videos',
        filterSupported: 'Supported tournament videos',
        filterTournament: 'Tournament videos',
        folder: 'Folder',
        idle: 'No folder selected',
        outsideWindow: 'Outside session window',
        pollInterval: 'Poll interval (s)',
        processing: 'Processing',
        running: 'Watching {folder}',
        selectFailed: 'Cannot read this folder',
        selectFolder: 'Select folder',
        skipped: 'Skipped',
        stop: 'Stop',
        uploaded: 'Uploaded',
        unsupported: 'Directory watching is not supported by this browser',
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

.auto-uploader__status {
    margin-bottom: 0.5rem;
}
</style>
