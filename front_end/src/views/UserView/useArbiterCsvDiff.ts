import { computed, onScopeDispose, ref, shallowRef, watch } from 'vue';
import type { ComputedRef, Ref, ShallowRef } from 'vue';

import { ArbiterCsvError, MAX_CSV_BYTES, parseArbiterCsv } from './arbiterCsv';
import type { ArbiterCsvResult, CsvIssue } from './arbiterCsv';
import { compareArbiterCsv } from './arbiterCsvDiff';

import type { VideoAbstract } from '@/utils/videoabstract';

interface ArbiterCsvDiffState {
    localVideos: ShallowRef<VideoAbstract[]>;
    issues: ShallowRef<CsvIssue[]>;
    failure: ShallowRef<CsvIssue | undefined>;
    reading: Ref<boolean>;
    filename: Ref<string>;
    hasCsv: ComputedRef<boolean>;
    importFile: (file: File) => Promise<void>;
    clear: () => void;
}

export function useArbiterCsvDiff(videos: Ref<VideoAbstract[]>, valid: Ref<boolean>, identity: Ref<string>, own: Ref<boolean>): ArbiterCsvDiffState {
    const csv = shallowRef<ArbiterCsvResult>();
    const localVideos = shallowRef<VideoAbstract[]>([]);
    const issues = shallowRef<CsvIssue[]>([]);
    const failure = shallowRef<CsvIssue>();
    const reading = ref(false);
    const filename = ref('');
    let importNumber = 0;

    function rebuild() {
        localVideos.value = [];
        issues.value = [];
        if (!csv.value || !valid.value || !own.value) return;
        const compared = compareArbiterCsv(csv.value.records, videos.value);
        localVideos.value = compared.localVideos;
        issues.value = [...csv.value.issues, ...compared.issues];
    }
    function clear() {
        importNumber++;
        csv.value = undefined;
        localVideos.value = [];
        issues.value = [];
        failure.value = undefined;
        filename.value = '';
        reading.value = false;
    }
    async function importFile(file: File) {
        clear();
        if (!own.value || !valid.value) return;
        const number = importNumber;
        reading.value = true;
        try {
            if (file.size > MAX_CSV_BYTES) throw new ArbiterCsvError({ code: 'limit' });
            const text = await file.text();
            if (number !== importNumber) return;
            csv.value = parseArbiterCsv(text);
            filename.value = file.name;
            rebuild();
        } catch (error) {
            if (number === importNumber) failure.value = error instanceof ArbiterCsvError ? error.issue : { code: 'read' };
        } finally {
            if (number === importNumber) reading.value = false;
        }
    }
    watch([videos, valid], rebuild, { flush: 'sync' });
    watch([identity, own], clear, { flush: 'sync' });
    onScopeDispose(clear);
    return { localVideos, issues, failure, reading, filename, hasCsv: computed(() => csv.value !== undefined), importFile, clear };
}
