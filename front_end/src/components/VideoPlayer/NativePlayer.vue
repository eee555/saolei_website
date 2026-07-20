<template>
    <div class="native-player">
        <ElResult v-if="loading" icon="info" :title="t('local.loading')" />
        <ElResult v-else-if="errorMessage" icon="error" :title="t('local.loadFailed')" :sub-title="errorMessage" />
        <div v-else-if="video !== null" class="native-player__content">
            <div class="native-player__stage" :class="{ 'native-player__stage--editing': isEditingCustomCounterConfig }">
                <CustomCounter
                    :video="video"
                    :current-ms="currentMs"
                    :config="customCounterConfig"
                />

                <CustomCounterSettings
                    v-if="isEditingCustomCounterConfig"
                    v-model="customCounterConfig"
                    class="native-player__config-editor"
                />
                <PlayerMain
                    v-else
                    :video="video"
                    :board="board"
                    :board-size="boardSize"
                    :current-ms="currentMs"
                    :cursor-position="cursorPosition"
                />
            </div>

            <div class="native-player__controls">
                <ProgressBar
                    v-model="currentMs"
                    class="native-player__progress"
                    :duration-ms="durationMs"
                />
                <ElCheckbox v-model="isEditingCustomCounterConfig">
                    {{ t('local.editCounter') }}
                </ElCheckbox>
            </div>
        </div>
        <ElResult v-else icon="info" :title="t('local.noVideo')" />
    </div>
</template>

<script setup lang="ts">
import { ElCheckbox, ElResult } from 'element-plus';
import { computed, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import CustomCounter from './CustomCounter.vue';
import CustomCounterSettings from './CustomCounterSettings.vue';
import PlayerMain from './PlayerMain.vue';
import ProgressBar from './ProgressBar.vue';
import { customCounterConfig } from './store';

import type { AnyVideo } from '@/utils/fileIO';
import { load_video_file } from '@/utils/fileIO';

const props = defineProps({
    src: { type: String, default: '' },
});

const i18nMessages = {
    'zh-cn': { local: {
        editCounter: '编辑计数器',
        loadFailed: '录像加载失败',
        loading: '正在加载录像',
        noVideo: '没有录像',
    } },
    en: { local: {
        editCounter: 'Edit counter',
        loadFailed: 'Failed to load video',
        loading: 'Loading video',
        noVideo: 'No video',
    } },
};

const { t } = useI18n({ messages: i18nMessages });

const loading = ref(false);
const errorMessage = ref('');
const video = shallowRef<AnyVideo | null>(null);
const board = ref<number[][]>([]);
const currentMs = ref(0);
const durationMs = ref(0);
const isEditingCustomCounterConfig = ref(false);
const cursor = ref({ x: 0, y: 0 });
const viewport = ref(readViewportSize());

const counterWidth = computed(() => {
    return Math.max(1, customCounterConfig.value.thWidth)
        + Math.max(1, customCounterConfig.value.tdWidth);
});

const boardSize = computed(() => {
    const column = Math.max(1, video.value?.column ?? 1);
    const row = Math.max(1, video.value?.row ?? 1);
    const isStacked = viewport.value.width <= 720;
    const tableWidth = isStacked ? 0 : counterWidth.value;
    const stageGap = isStacked ? 0 : 12;
    const horizontalChrome = 50 + tableWidth + stageGap + 28;
    const verticalChrome = 290;
    const availableWidth = Math.max(1, viewport.value.width * 0.95 - horizontalChrome);
    const availableHeight = Math.max(1, viewport.value.height - verticalChrome);
    return Math.max(1, Math.floor(Math.min(28, availableWidth / column, availableHeight / row)));
});

const cursorPosition = computed(() => {
    const pixSize = video.value?.pix_size ?? 0;
    if (pixSize <= 0 || !Number.isFinite(cursor.value.x) || !Number.isFinite(cursor.value.y)) return undefined;
    return {
        rowIndex: cursor.value.y / pixSize,
        columnIndex: cursor.value.x / pixSize,
    };
});

let abortController: AbortController | null = null;
watch(() => props.src, (src) => {
    void loadVideo(src);
}, { immediate: true });

watch(currentMs, () => {
    updateVideoState();
});

onMounted(() => {
    window.addEventListener('resize', updateViewportSize);
});

async function loadVideo(src: string) {
    cleanupVideo();
    errorMessage.value = '';
    board.value = [];
    currentMs.value = 0;
    durationMs.value = 0;

    if (src === '') return;

    loading.value = true;
    abortController?.abort();
    abortController = new AbortController();

    try {
        const response = await fetch(src, { signal: abortController.signal });
        if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);

        const parsed = load_video_file(await response.arrayBuffer(), filenameFromSrc(src));
        video.value = parsed;
        durationMs.value = Math.max(0, Math.trunc(parsed.rtime_ms));
        currentMs.value = 0;
        updateVideoState();
    } catch (error) {
        if ((error as DOMException).name !== 'AbortError') {
            errorMessage.value = error instanceof Error ? error.message : String(error);
        }
    } finally {
        loading.value = false;
    }
}

function updateVideoState() {
    const currentVideo = video.value;
    if (currentVideo === null) return;

    currentVideo.current_time = Math.min(currentMs.value, durationMs.value) / 1000;
    board.value = normalizeBoard(currentVideo.game_board);
    cursor.value = { x: currentVideo.x_y.x, y: currentVideo.x_y.y };
}

function normalizeBoard(value: unknown): number[][] {
    if (!Array.isArray(value)) return [];
    return value.map((row) => {
        return Array.isArray(row) ? row.map((cell) => Number(cell)) : [];
    });
}

function filenameFromSrc(src: string) {
    try {
        const url = new URL(src, window.location.href);
        return url.searchParams.get('id') ?? url.pathname.split('/').pop() ?? 'video.avf';
    } catch {
        return src.split('/').pop() ?? 'video.avf';
    }
}

function cleanupVideo() {
    video.value?.free();
    video.value = null;
}

function readViewportSize() {
    if (typeof window === 'undefined') return { height: 720, width: 1280 };
    return { height: window.innerHeight, width: window.innerWidth };
}

function updateViewportSize() {
    viewport.value = readViewportSize();
}

onBeforeUnmount(() => {
    abortController?.abort();
    window.removeEventListener('resize', updateViewportSize);
    cleanupVideo();
});
</script>

<style scoped>
.native-player {
    min-width: min(92vw, 520px);
    max-width: calc(95vw - 50px);
    overflow: hidden;
}

.native-player__content {
    display: flex;
    flex-direction: column;
    gap: 12px;
    width: 100%;
    min-width: 0;
    max-width: calc(95vw - 50px);
    max-height: calc(100vh - 170px);
    overflow: hidden;
}

.native-player__controls {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
}

.native-player__stage {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    width: 100%;
    min-width: 0;
    max-width: 100%;
    overflow-x: auto;
    overflow-y: hidden;
}

.native-player__stage--editing {
    align-items: stretch;
    justify-content: flex-start;
}

.native-player__config-editor {
    flex: 0 0 auto;
    align-self: stretch;
    max-height: calc(100vh - 290px);
}

@media (width <= 720px) {
    .native-player__stage {
        flex-direction: column;
        align-items: center;
    }

    .native-player__stage--editing {
        align-items: flex-start;
    }
}

.native-player__progress {
    flex: 1 1 260px;
    min-width: 160px;
}
</style>
