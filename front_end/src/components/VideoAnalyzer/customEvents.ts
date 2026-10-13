import { createCounterEvaluator, parseCounterExpression, selectCounterEvents } from './counter';
import type { CounterEvent } from './counter';

export const eventMarkerShapes = ['circle', 'square', 'triangle', 'diamond', 'cross'] as const;
export const eventLineStyles = ['solid', 'dash', 'dot'] as const;

export interface CustomEventDefinition {
    key: string;
    expression: string;
    type: 'pulse' | 'sustained';
    color: string;
    marker: { shape: typeof eventMarkerShapes[number]; size: number; opacity: number };
    line: { style: typeof eventLineStyles[number]; width: number; opacity: number };
}

export interface EventPulse {
    timeMs: number;
    eventIndex: number;
}

export interface EventSpan {
    startMs: number;
    endMs: number;
    renderEndMs: number;
    startEventIndex: number;
    lastEventIndex: number;
}

export interface PreparedCustomEvent {
    pulses: EventPulse[];
    spans: EventSpan[];
}

export function defaultCustomEvent(): CustomEventDefinition {
    return { key: '', expression: '', type: 'pulse', color: '#e15759', marker: { shape: 'circle', size: 8, opacity: 1 }, line: { style: 'solid', width: 2, opacity: 1 } };
}

export function eventOccurs(value: unknown): boolean {
    return (typeof value === 'boolean' || typeof value === 'number' || typeof value === 'string') && Boolean(value);
}

export function prepareCustomEvent(definition: CustomEventDefinition, snapshots: CounterEvent[], durationMs: number): PreparedCustomEvent {
    const result: PreparedCustomEvent = { pulses: [], spans: [] };
    let evaluate: (index: number) => unknown;
    try {
        evaluate = createCounterEvaluator(parseCounterExpression(definition.expression), snapshots);
    } catch {
        return result;
    }
    let active: EventSpan | null = null;
    for (const [index, snapshot] of snapshots.entries()) {
        let occurs = false;
        try {
            occurs = eventOccurs(evaluate(index));
        } catch {
            // A failed sample ends a sustained event just like a false result.
        }
        if (definition.type === 'pulse') {
            if (occurs) result.pulses.push({ timeMs: snapshot.timeMs, eventIndex: snapshot.eventIndex });
        } else if (occurs) {
            active ??= { startMs: snapshot.timeMs, endMs: durationMs, renderEndMs: snapshot.timeMs, startEventIndex: snapshot.eventIndex, lastEventIndex: snapshot.eventIndex };
            active.renderEndMs = snapshot.timeMs;
            active.lastEventIndex = snapshot.eventIndex;
        } else if (active !== null) {
            active.endMs = snapshot.timeMs;
            result.spans.push(active);
            active = null;
        }
    }
    if (active !== null) result.spans.push({ ...active, endMs: durationMs, renderEndMs: durationMs });
    return result;
}

export function prepareCustomEvents(definitions: CustomEventDefinition[], events: CounterEvent[], durationMs: number): Map<string, PreparedCustomEvent> {
    const snapshots = selectCounterEvents(events, 'continuous', durationMs);
    return new Map(definitions.map((definition) => [definition.key, prepareCustomEvent(definition, snapshots, durationMs)]));
}

export function eventLineDash(style: CustomEventDefinition['line']['style']): string {
    return style === 'dash' ? '6 3' : style === 'dot' ? '1 3' : 'none';
}
