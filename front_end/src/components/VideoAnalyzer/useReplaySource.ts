import { computed, shallowRef, toValue, watch } from 'vue';
import type { ComputedRef, MaybeRefOrGetter, ShallowRef } from 'vue';

import { parseReplay } from './replayParser';
import type { ReplaySource, ReplayVideo } from './replayParser';

export interface ReplaySourceState {
    video: ShallowRef<ReplayVideo | null>;
    errorMessage: ShallowRef<string>;
    durationMs: ComputedRef<number>;
    globalBoard: ComputedRef<number[][] | null>;
    createExportVideo: () => ReplayVideo;
}

export function useReplaySource(source: MaybeRefOrGetter<ReplaySource | null>): ReplaySourceState {
    const video = shallowRef<ReplayVideo | null>(null);
    const errorMessage = shallowRef('');
    const durationMs = computed(() => video.value?.rtime_ms ?? 0);
    const globalBoard = computed(() => (video.value === null ? null : video.value.board as number[][]));
    watch(() => toValue(source), (input, _previous, onCleanup) => {
        errorMessage.value = '';
        if (input === null) return;
        try {
            const parsed = parseReplay(input.data, input.filename, input.software);
            onCleanup(() => {
                video.value = null;
                parsed.free();
            });
            video.value = parsed;
        } catch (error) {
            errorMessage.value = error instanceof Error ? error.message : String(error);
        }
    }, { immediate: true, flush: 'sync' });
    return { video,
        durationMs,
        globalBoard,
        errorMessage,
        createExportVideo: () => {
            const input = toValue(source);
            if (input === null || video.value === null) throw new Error('Replay is not loaded');
            return parseReplay(input.data, input.filename, input.software);
        } };
}
