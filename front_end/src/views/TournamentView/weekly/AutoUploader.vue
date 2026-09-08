<template>
    <div class="auto-uploader">
        <div class="auto-uploader__controls">
            <div class="auto-uploader__control">
                <span class="auto-uploader__label">{{ t('local.folder') }}</span>
                <ElButton type="primary" :disabled="!canSelectDirectory" :loading="selectingDirectory" @click="selectDirectory">
                    <BaseIconUpload />&nbsp;{{ directoryName || t('local.selectFolder') }}
                </ElButton>
                <ElButton v-if="running" :disabled="processingQueue" @click="stopWatching">
                    {{ t('local.stop') }}
                </ElButton>
            </div>
            <div class="auto-uploader__control">
                <span class="auto-uploader__label">{{ t('local.pollInterval') }}</span>
                <ElInputNumber v-model="pollIntervalSeconds" :min="1" :max="300" :step="1" :disabled="running" size="small" controls-position="right" />
            </div>
            <div class="auto-uploader__control">
                <span class="auto-uploader__label">{{ t('local.filter') }}</span>
                <ElSelect v-model="filterLevel" size="small" style="width: 180px">
                    <ElOption v-for="option in filterOptions" :key="option.value" :label="t(option.labelKey)" :value="option.value" />
                </ElSelect>
            </div>
        </div>

        <div class="auto-uploader__status text">
            {{ statusText }}
            <span v-if="scannedCount > 0">
                {{ t('common.punct.comma') }}
                {{ t('local.stat', { scanned: scannedCount, uploaded: uploadedCount, skipped: skippedCount, failed: failedCount }) }}
            </span>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ElButton, ElInputNumber, ElMessage, ElOption, ElSelect } from 'element-plus';
import { computed, onBeforeUnmount, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import { BaseIconUpload } from '@/components/common/icon';
import type { UploadEntry } from '@/components/VideoUpload/utils';
import { fileCollide, isUploadableStatus, prepareUploadEntry, uploadEntry } from '@/components/VideoUpload/utils';
import { globalNow } from '@/utils/datetime';
import { createDirectoryNewFileEmitter } from '@/utils/fileIO';
import type { DirectoryNewFileEmitter, DirectoryNewFileEvent } from '@/utils/fileIO';
import { Tournament, TournamentParticipant } from '@/utils/tournaments';
import type { VideoAbstract } from '@/utils/videoabstract';
import { isWeeklyClassicScoreMode, WeeklyTournamentFormat } from '@/utils/weekly';

const props = defineProps({
    tournament: { type: Tournament, required: true },
    participant: { type: TournamentParticipant, required: true },
    videos: { type: Array<VideoAbstract>, default: () => [] },
});
const emit = defineEmits<{
    uploaded: [video: VideoAbstract];
}>();
const WeeklyAutoUploadFilter = {
    Tournament: 'tournament',
    Supported: 'supported',
    ScoreRefreshing: 'scoreRefreshing',
} as const;
type WeeklyAutoUploadFilter = typeof WeeklyAutoUploadFilter[keyof typeof WeeklyAutoUploadFilter];

interface DirectoryPickerWindow extends Window {
    showDirectoryPicker?: (options?: { mode?: 'read' | 'readwrite' }) => Promise<FileSystemDirectoryHandle>;
}

const directory = ref<FileSystemDirectoryHandle | null>(null);
const directoryName = ref('');
const emitter = ref<DirectoryNewFileEmitter | null>(null);
const selectingDirectory = ref(false);
const filterLevel = ref<WeeklyAutoUploadFilter>(WeeklyAutoUploadFilter.Supported);
const pollIntervalSeconds = ref(3);
const pendingFiles: File[] = [];
const processedEntries: UploadEntry[] = [];
const processingQueue = ref(false);
const uploadedCount = ref(0);
const failedCount = ref(0);
const skippedCount = ref(0);
const scannedCount = ref(0);

const filterOptions = [
    { value: WeeklyAutoUploadFilter.Tournament, labelKey: 'local.filterTournament' },
    { value: WeeklyAutoUploadFilter.Supported, labelKey: 'local.filterSupported' },
    { value: WeeklyAutoUploadFilter.ScoreRefreshing, labelKey: 'local.filterScoreRefreshing' },
] as const;

const directoryPickerSupported = computed(() => typeof window !== 'undefined' && typeof (window as DirectoryPickerWindow).showDirectoryPicker === 'function');
const participantWindowOpen = computed(() => {
    if (!props.participant.start_time || !props.participant.end_time) return false;
    return props.participant.start_time <= globalNow.value && globalNow.value < props.participant.end_time;
});
const running = computed(() => emitter.value?.running ?? false);
const canSelectDirectory = computed(() => directoryPickerSupported.value && participantWindowOpen.value);
const statusText = computed(() => {
    if (!directoryPickerSupported.value) return t('local.unsupported');
    if (!participantWindowOpen.value) return t('local.outsideWindow');
    if (running.value) return t('local.running', { folder: directoryName.value });
    if (directoryName.value !== '') return t('local.stopped', { folder: directoryName.value });
    return t('local.idle');
});

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
        if (file) await processFile(file);
    }
    processingQueue.value = false;
}

async function processFile(file: File) {
    scannedCount.value += 1;
    let entry: UploadEntry;
    try {
        entry = await prepareUploadEntry(file);
    } catch (error) {
        console.error(error);
        entry = {
            hash: `${file.name}-${Date.now()}`,
            file,
            status: 'parse',
        };
    }

    if (processedEntries.some((oldEntry) => fileCollide(oldEntry, entry))) {
        skippedCount.value += 1;
        logUpload('skip duplicate', entry);
        return;
    }
    processedEntries.push(entry);

    if (!isUploadableStatus(entry.status)) {
        skippedCount.value += 1;
        logUpload('skip invalid status', entry);
        return;
    }

    if (!matchesFilter(entry)) {
        skippedCount.value += 1;
        logUpload('skip filter', entry);
        return;
    }

    logUpload('upload start', entry);
    try {
        await uploadEntry(entry);
        if (entry.status === 'success' && entry.stat !== undefined) {
            uploadedCount.value += 1;
            emit('uploaded', entry.stat);
            logUpload('upload success', entry);
        } else {
            failedCount.value += 1;
            logUpload('upload failed', entry);
        }
    } catch (error) {
        console.error(error);
        failedCount.value += 1;
        logUpload('upload error', entry);
    }
}

function matchesFilter(entry: UploadEntry): boolean {
    if (!isTournamentVideo(entry)) return false;
    if (filterLevel.value === WeeklyAutoUploadFilter.Tournament) return true;
    if (!isWeeklySupportedVideo(entry)) return false;
    if (filterLevel.value === WeeklyAutoUploadFilter.Supported) return true;
    return canRefreshWeeklyScore(entry);
}

function isTournamentVideo(entry: UploadEntry): boolean {
    if (entry.video === undefined) return false;
    return entry.video.race_identifier.split(',').map((identifier) => identifier.trim()).includes(props.participant.token);
}

function isWeeklySupportedVideo(entry: UploadEntry | VideoAbstract): boolean {
    const stat = getStat(entry);
    if (stat === undefined) return false;
    if (props.tournament.weeklyData?.tournament_format !== WeeklyTournamentFormat.Classic) return false;
    return (stat.level === 'i' || stat.level === 'e') && isWeeklyClassicScoreMode(stat.mode);
}

function canRefreshWeeklyScore(entry: UploadEntry): boolean {
    if (entry.stat === undefined || !isWeeklySupportedVideo(entry)) return false;
    const { level } = entry.stat;
    if (level !== 'i' && level !== 'e') return false;
    const count = level === 'i' ? 5 : 2;
    const defaultTime = level === 'i' ? 60000 : 240000;
    const currentTimes = props.videos.
        filter((video) => video.level === level && isWeeklySupportedVideo(video)).
        map((video) => video.timems).
        sort((left, right) => left - right);
    const currentBoundary = currentTimes.length >= count ? currentTimes[count - 1] : defaultTime;
    return entry.stat.timems < currentBoundary;
}

function getStat(entry: UploadEntry | VideoAbstract): VideoAbstract | undefined {
    return 'file' in entry ? entry.stat : entry;
}

function logUpload(action: string, entry: UploadEntry) {
    console.info('[WeeklyAutoUploader]', action, {
        file: entry.file.name,
        status: entry.status,
        level: entry.stat?.level,
        mode: entry.stat?.mode,
        timems: entry.stat?.timems,
        raceIdentifier: entry.video?.race_identifier,
    });
}

watch(canSelectDirectory, (canSelect) => {
    if (!canSelect) stopWatching();
});

onBeforeUnmount(stopWatching);

const i18nMessages = {
    'zh-cn': { local: {
        filter: '筛选级别',
        filterScoreRefreshing: '刷新成绩的录像',
        filterSupported: '比赛支持的录像',
        filterTournament: '比赛录像',
        folder: '文件夹',
        idle: '未选择文件夹',
        outsideWindow: '不在参赛时间内',
        pollInterval: '轮询周期（秒）',
        running: '正在监听 {folder}',
        selectFailed: '无法读取该文件夹',
        selectFolder: '选择文件夹',
        stat: '已扫描 {scanned}，已上传 {uploaded}，已跳过 {skipped}，失败 {failed}',
        stop: '停止',
        unsupported: '当前浏览器不支持目录监听',
    } },
    en: { local: {
        filter: 'Filter',
        filterScoreRefreshing: 'Score-improving videos',
        filterSupported: 'Supported tournament videos',
        filterTournament: 'Tournament videos',
        folder: 'Folder',
        idle: 'No folder selected',
        outsideWindow: 'Outside session window',
        pollInterval: 'Poll interval (s)',
        running: 'Watching {folder}',
        selectFailed: 'Cannot read this folder',
        selectFolder: 'Select folder',
        stat: 'Scanned {scanned}, uploaded {uploaded}, skipped {skipped}, failed {failed}',
        stop: 'Stop',
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
