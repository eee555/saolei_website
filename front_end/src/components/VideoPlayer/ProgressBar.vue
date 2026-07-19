<template>
    <div class="progress-bar">
        <ElButton circle :icon="RefreshLeft" :title="t('local.restart')" @click="restart" />
        <ElButton
            class="progress-bar__play"
            circle
            :icon="isPlaying ? VideoPause : VideoPlay"
            :title="isPlaying ? t('local.pause') : t('local.play')"
            @click="togglePlay"
        />
        <ElButton :title="t('local.step')" @click="stepForward">
            +0.1s
        </ElButton>
        <ElSlider
            v-model="currentMs" class="progress-bar__slider" :min="0" :max="durationMs"
            :step="step" :format-tooltip="formatSeconds" @change="syncPlaybackAnchor"
        />
        <ElSelect v-model="playbackRate" class="progress-bar__speed" :title="t('local.speed')">
            <ElOption v-for="rate in playbackRates" :key="rate" :value="rate" :label="`${rate}x`" />
        </ElSelect>
    </div>
</template>

<script setup lang="ts">
import { RefreshLeft, VideoPause, VideoPlay } from '@element-plus/icons-vue';
import { ElButton, ElOption, ElSelect, ElSlider } from 'element-plus';
import { onBeforeUnmount, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

const props = defineProps({
    durationMs: { type: Number, required: true },
    step: { type: Number, default: 10 },
});

const i18nMessages = {
    'zh-cn': { local: {
        pause: '暂停',
        play: '播放',
        restart: '重新开始',
        speed: '播放速度',
        step: '前进 0.1 秒',
    } },
    en: { local: {
        pause: 'Pause',
        play: 'Play',
        restart: 'Restart',
        speed: 'Playback speed',
        step: 'Step 0.1 seconds',
    } },
};

const { t } = useI18n({ messages: i18nMessages });

const playbackRates = [0.5, 1, 1.5, 2, 4];

const currentMs = defineModel<number>({ required: true });
const isPlaying = ref(false);
const playbackRate = ref(1);

let animationFrameId = 0;
let startedAt = 0;
let startedFrom = 0;

watch(() => props.durationMs, (durationMs) => {
    currentMs.value = clampTime(currentMs.value, durationMs);
    if (currentMs.value >= durationMs) stopPlayback();
});

function formatSeconds(value: number) {
    return `${(value / 1000).toFixed(2)}s`;
}

function togglePlay() {
    if (isPlaying.value) {
        stopPlayback();
    } else {
        startPlayback();
    }
}

function startPlayback() {
    if (props.durationMs <= 0) return;
    if (currentMs.value >= props.durationMs) currentMs.value = 0;
    isPlaying.value = true;
    syncPlaybackAnchor();
    animationFrameId = requestAnimationFrame(tick);
}

function stopPlayback() {
    isPlaying.value = false;
    if (animationFrameId !== 0) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = 0;
    }
}

function tick(now: number) {
    if (!isPlaying.value) return;

    currentMs.value = clampTime(startedFrom + (now - startedAt) * playbackRate.value, props.durationMs);
    if (currentMs.value >= props.durationMs) {
        stopPlayback();
        return;
    }
    animationFrameId = requestAnimationFrame(tick);
}

function restart() {
    stopPlayback();
    currentMs.value = 0;
}

function stepForward() {
    stopPlayback();
    currentMs.value = clampTime(currentMs.value + 100, props.durationMs);
}

function syncPlaybackAnchor() {
    startedAt = performance.now();
    startedFrom = currentMs.value;
}

function clampTime(value: number, durationMs: number) {
    return Math.min(Math.max(0, value), Math.max(0, durationMs));
}

onBeforeUnmount(() => {
    stopPlayback();
});
</script>

<style scoped>
.progress-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
}

.progress-bar__slider {
    flex: 1 1 260px;
    min-width: 160px;
}

.progress-bar__speed {
    width: 86px;
}
</style>
