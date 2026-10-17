import { onScopeDispose, ref, shallowRef } from 'vue';
import type { Ref, ShallowRef } from 'vue';

import type { ReplaySource } from '@/components/VideoAnalyzer/replayParser';

const formats = { avf: 'a', evf: 'e', mvf: 'm', rmv: 'r' } as const;

export interface LocalReplaySourceState {
    source: ShallowRef<ReplaySource | null>;
    filename: Ref<string>;
    loading: Ref<boolean>;
    errorMessage: Ref<string>;
    selectFiles: (files: File[]) => Promise<void>;
}

export function useLocalReplaySource(): LocalReplaySourceState {
    const source = shallowRef<ReplaySource | null>(null);
    const filename = ref('');
    const loading = ref(false);
    const errorMessage = ref('');
    let requestId = 0;
    onScopeDispose(() => {
        requestId++;
        source.value = null;
    });

    async function selectFiles(files: File[]): Promise<void> {
        if (files.length === 0) return;
        const currentRequest = ++requestId;
        source.value = null;
        errorMessage.value = '';
        loading.value = false;
        filename.value = files.length === 1 ? files[0].name : '';
        if (files.length !== 1) {
            errorMessage.value = 'oneFileOnly';
            return;
        }
        const [file] = files;
        const extension = file.name.split('.').pop()?.toLowerCase() ?? '';
        if (!Object.hasOwn(formats, extension)) {
            errorMessage.value = 'unsupportedFormat';
            return;
        }
        loading.value = true;
        try {
            const data = await file.arrayBuffer();
            if (currentRequest !== requestId) return;
            source.value = { data, filename: file.name, software: formats[extension as keyof typeof formats] };
        } catch (error) {
            if (currentRequest === requestId) errorMessage.value = error instanceof Error ? error.message : String(error);
        } finally {
            if (currentRequest === requestId) loading.value = false;
        }
    }

    return { source, filename, loading, errorMessage, selectFiles };
}
