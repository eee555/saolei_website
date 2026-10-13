import { createLinearScale, getDataDomain } from '@putianyi888/vue3-plots';
import type { PlotPoint } from '@putianyi888/vue3-plots';

import { counterValue } from './counter';
import type { PreparedCounter } from './counter';

export interface TimelineTrack {
    key: string;
    color: string;
}

export interface TimelineSlotSettings {
    name: string;
    height: number;
}

export interface TimelineConfig {
    // Keep the persisted keys for existing configurations; the UI calls these plots.
    slots: TimelineTrack[][];
    slotSettings: TimelineSlotSettings[];
}

export interface TimeWindow {
    startMs: number;
    endMs: number;
}

export const timelinePalette = ['#4e79a7', '#f28e2c', '#e15759', '#76b7b2', '#59a14f', '#edc949', '#af7aa1', '#ff9da7', '#9c755f', '#bab0ab'];
export const timelinePadding = { left: 4, right: 4, top: 8, bottom: 8 };
export const minimumSlotHeight = 80;

export function defaultTimelineConfig(): TimelineConfig {
    const config: TimelineConfig = { slots: [[], []], slotSettings: [1, 2].map((index) => ({ name: `Plot ${index}`, height: 160 })) };
    addTimelineTrack(config, 0, 'Bvs');
    addTimelineTrack(config, 0, 'Ces');
    addTimelineTrack(config, 1, 'Mov');
    return config;
}

export function addTimelineTrack(config: TimelineConfig, slotIndex: number, key: string): void {
    const slot = config.slots[slotIndex];
    if (slot === undefined) return;
    const counts = timelinePalette.map((color) => slot.filter((track) => track.color === color).length);
    const color = timelinePalette[counts.indexOf(Math.min(...counts))];
    slot.push({ key, color });
}

export function clampTimeWindow(window: TimeWindow, durationMs: number): TimeWindow {
    if (durationMs <= 0) return { startMs: 0, endMs: 0 };
    const length = Math.min(durationMs, Math.max(Math.min(1, durationMs), window.endMs - window.startMs));
    const startMs = Math.max(0, Math.min(durationMs - length, window.startMs));
    return { startMs, endMs: startMs + length };
}

export function panTimeWindow(window: TimeWindow, offsetMs: number, durationMs: number): TimeWindow {
    return clampTimeWindow({ startMs: window.startMs + offsetMs, endMs: window.endMs + offsetMs }, durationMs);
}

export function zoomTimeWindow(window: TimeWindow, factor: number, anchor: number, durationMs: number): TimeWindow {
    const normalized = clampTimeWindow(window, durationMs);
    const ratio = Math.max(0, Math.min(1, anchor));
    const length = Math.min(durationMs, Math.max(Math.min(1, durationMs), (normalized.endMs - normalized.startMs) * factor));
    const startMs = normalized.startMs + (normalized.endMs - normalized.startMs - length) * ratio;
    return clampTimeWindow({ startMs, endMs: startMs + length }, durationMs);
}

export function timeAtPixel(window: TimeWindow, x: number, left: number, width: number): number {
    const boundedX = Math.max(left, Math.min(left + width, x));
    return createLinearScale(left, left + width, window.startMs, window.endMs)(boundedX);
}

export function timelinePoints(counter: PreparedCounter, durationMs: number): PlotPoint[] {
    if (counter.error !== '' || counter.samples.length === 0) return [];
    const points = counter.samples.map((sample) => ({ x: sample.timeMs, y: sample.value }));
    if (points[0].x > 0) points.unshift({ x: 0, y: counterValue(counter.samples, 0) });
    if (points[points.length - 1].x < durationMs) points.push({ x: durationMs, y: counterValue(counter.samples, durationMs) });
    return points;
}

export function timelineYDomain(tracks: TimelineTrack[], counters: Map<string, PreparedCounter>): { yMin: number; yMax: number } {
    const points = tracks.flatMap((track) => counters.get(track.key)?.samples.map((sample) => ({ x: sample.timeMs, y: sample.value })) ?? []);
    const { yMin, yMax } = getDataDomain(points);
    return { yMin, yMax };
}
