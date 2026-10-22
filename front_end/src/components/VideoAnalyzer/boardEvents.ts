import { bisector } from 'd3-array';

import type { CustomEventDefinition, EventPulse, EventSpan, PreparedCustomEvent } from './customEvents';
import type { ReplayMouseTraceEvent } from './mouseTrace';

export interface BoardEventSettings {
    visible: boolean;
    keys: string[];
    timeRange: 'all' | 'past';
    arrowSpacing: number;
    arrowSize: number;
    arrowShape: 'triangle' | 'open';
}

export interface EventPoint { x: number; y: number }
export interface EventArrow extends EventPoint { angle: number }
export interface BoardEventPulse extends EventPoint { pulse: EventPulse }
export interface BoardEventPath { points: EventPoint[]; span: EventSpan }
export interface BoardEventGeometry {
    definition: CustomEventDefinition;
    pulses: BoardEventPulse[];
    paths: BoardEventPath[];
}

export function defaultBoardEventSettings(): BoardEventSettings {
    return { visible: true, keys: ['pluck'], timeRange: 'all', arrowSpacing: 32, arrowSize: 8, arrowShape: 'triangle' };
}

const byTime = bisector<ReplayMouseTraceEvent, number>((event) => Math.round(event.timeMs));
const byIndex = bisector<ReplayMouseTraceEvent, number>((event) => event.eventIndex);
const validPosition = (event: ReplayMouseTraceEvent) => Number.isFinite(event.row) && Number.isFinite(event.column) && event.row >= 0 && event.column >= 0;

export function boardEventGeometry(definitions: CustomEventDefinition[], prepared: Map<string, PreparedCustomEvent>, mouse: ReplayMouseTraceEvent[], keys: string[], currentMs = Infinity, currentEventIndex: number | null = null): BoardEventGeometry[] {
    const limit = Math.min(byTime.right(mouse, currentMs), currentEventIndex === null ? mouse.length : byIndex.right(mouse, currentEventIndex));
    const position = (event: ReplayMouseTraceEvent): EventPoint => ({ x: event.column, y: event.row });
    return definitions.filter((definition) => keys.includes(definition.key)).map((definition) => {
        const data = prepared.get(definition.key);
        const pulses: BoardEventPulse[] = [];
        const paths: BoardEventPath[] = [];
        for (const pulse of data?.pulses ?? []) {
            const index = byIndex.left(mouse, pulse.eventIndex);
            const event = mouse[index];
            if (pulse.timeMs <= currentMs && index < limit && event.eventIndex === pulse.eventIndex && validPosition(event)) pulses.push({ ...position(event), pulse });
        }
        for (const span of data?.spans ?? []) {
            // The millisecond snapshot identifies the span, but its trace retains all native mouse points.
            const start = byTime.left(mouse, span.startMs);
            const end = Math.min(limit, byTime.right(mouse, span.renderEndMs), byIndex.right(mouse, span.lastEventIndex));
            let points: EventPoint[] = [];
            for (let index = start; index < end; index++) {
                const event = mouse[index];
                if (validPosition(event)) points.push(position(event));
                else if (points.length > 0) {
                    paths.push({ points, span });
                    points = [];
                }
            }
            if (points.length > 0) paths.push({ points, span });
        }
        return { definition, pulses, paths };
    });
}

export function eventDirectionArrows(points: EventPoint[], spacing: number): EventArrow[] {
    if (!Number.isFinite(spacing) || spacing < 1) return [];
    const arrows: EventArrow[] = [];
    let travelled = 0;
    let next = spacing;
    let last: EventArrow | null = null;
    for (let index = 1; index < points.length; index++) {
        const start = points[index - 1];
        const end = points[index];
        const dx = end.x - start.x;
        const dy = end.y - start.y;
        const length = Math.hypot(dx, dy);
        if (length === 0) continue;
        const angle = Math.atan2(dy, dx) * 180 / Math.PI;
        while (next <= travelled + length) {
            const ratio = (next - travelled) / length;
            arrows.push({ x: start.x + dx * ratio, y: start.y + dy * ratio, angle });
            next += spacing;
        }
        travelled += length;
        last = { ...end, angle };
    }
    if (arrows.length === 0 && last !== null) arrows.push(last);
    return arrows;
}

export function updateBoardEventKeys(keys: string[], originalKey: string, newKey: string | null): string[] {
    return newKey === null ? keys.filter((key) => key !== originalKey) : keys.map((key) => (key === originalKey ? newKey : key));
}
