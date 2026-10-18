import { computed, toValue } from 'vue';
import type { ComputedRef, MaybeRefOrGetter } from 'vue';

import type { AnalyzerConfig } from './config';
import { prepareCounters } from './counter';
import type { CounterEvent, PreparedCounter } from './counter';
import { prepareCustomEvents } from './customEvents';
import type { PreparedCustomEvent } from './customEvents';

export function usePreparedAnalysis(config: MaybeRefOrGetter<AnalyzerConfig>, events: MaybeRefOrGetter<CounterEvent[]>, durationMs: MaybeRefOrGetter<number>): { preparedCounters: ComputedRef<Map<string, PreparedCounter>>; preparedEvents: ComputedRef<Map<string, PreparedCustomEvent>> } {
    // Keep unrelated root-config replacements from invalidating full-replay sampling.
    const rows = computed(() => toValue(config).counter.rows);
    const definitions = computed(() => toValue(config).customEvents);
    const preparedCounters = computed(() => prepareCounters(rows.value, toValue(events), toValue(durationMs)));
    const preparedEvents = computed(() => prepareCustomEvents(definitions.value, toValue(events), toValue(durationMs)));
    return { preparedCounters, preparedEvents };
}
