import { isAxiosError, isCancel } from 'axios';
import { ref, shallowRef, toValue, watch } from 'vue';
import type { MaybeRefOrGetter, Ref, ShallowRef } from 'vue';

import $axios from '@/http';

export interface SiteReplayRanking {
    ranking: 'saolei' | 'pb' | 'pluck';
    stat: string;
    nf: boolean;
    rank: number;
}

export interface SiteReplayInfo {
    video: { id: number; player: number; upload_time: string };
    expanded_video: Record<string, unknown>;
    tournament_ids: number[];
    filename: string;
    rankings: SiteReplayRanking[];
}

export interface SiteReplayInfoState {
    info: ShallowRef<SiteReplayInfo | null>;
    loading: Ref<boolean>;
    errorMessage: Ref<string>;
}

export function useSiteReplayInfo(id: MaybeRefOrGetter<string>): SiteReplayInfoState {
    const info = shallowRef<SiteReplayInfo | null>(null);
    const loading = ref(false);
    const errorMessage = ref('');
    watch(() => toValue(id), async (videoId, _previous, onCleanup) => {
        const controller = new AbortController();
        info.value = null;
        errorMessage.value = '';
        loading.value = true;
        onCleanup(() => {
            controller.abort();
            info.value = null;
        });
        try {
            const response = await $axios.get<SiteReplayInfo>(`/api/common/video/${encodeURIComponent(videoId)}/analyzer-info`, { signal: controller.signal });
            if (!controller.signal.aborted) info.value = response.data;
        } catch (error) {
            if (controller.signal.aborted || isCancel(error)) return;
            errorMessage.value = isAxiosError(error) && error.response !== undefined
                ? `${error.response.status} ${error.response.statusText}`.trim()
                : error instanceof Error ? error.message : String(error);
        } finally {
            if (!controller.signal.aborted) loading.value = false;
        }
    }, { immediate: true, flush: 'sync' });
    return { info, loading, errorMessage };
}
