import $axios from '@/http';
import { ms_to_s } from '@/utils';
import { MS_Levels } from '@/utils/ms_const';
import type { MS_Level } from '@/utils/ms_const';
import { STNB_COEFFICIENTS } from '@/utils/stnb';

export type TopStat = 't' | 'b' | 's';
export type TopField = `${'std' | 'nf'}:${MS_Level}${TopStat}`;
export const topLevels = MS_Levels;
export const topStats = ['t', 'b', 's'] as const;
export const topStatNames = { t: 'time', b: 'bvs', s: 'stnb' } as const;
export const topAxes = topLevels.flatMap((level) => topStats.map((stat) => ({ level, stat })));

export interface TopVideo {
    value: number;
    video_id: number;
}
export interface TopRankingPlayer {
    player_id: number;
    records: TopRecords;
}
export interface TopRecord {
    videos: TopVideo[];
}
export interface TopAnchor {
    value: number;
    sample_count: number;
}
export type TopRecords = Partial<Record<TopField, TopRecord>>;
export type TopAnchors = Partial<Record<TopField, TopAnchor>>;
export const softFields = ['lsf', 'std:b', 'std:i', 'std:e', 'std:sum', 'nf:b', 'nf:i', 'nf:e', 'nf:sum'] as const;
export type SoftField = typeof softFields[number];
export interface SoftRankingResult {
    count: number;
    players: TopRankingPlayer[];
}
const softWeights = { b: { t: 28, b: 48, s: 24 }, i: { t: 34, b: 34, s: 32 }, e: { t: 33, b: 33, s: 34 } };
const levelWeights = { b: 6, i: 14, e: 20 };
const gradeNodes = [0, 1 / 100, 1 / 60, 1 / 55, 1 / 50, 1 / 45, 1 / 40, 1 / 35, 1 / 30, 1 / 25];
const gradeInverseWidths = gradeNodes.slice(1).map((node, index) => 1 / (node - gradeNodes[index]));

export function topField(nf: boolean, level: MS_Level, stat: TopStat): TopField {
    return `${nf ? 'nf' : 'std'}:${level}${stat}`;
}

export function missingTopValue(stat: TopStat): number {
    return stat === 't' ? 999999 : 0;
}

export function topMean(record: TopRecord | undefined, stat: TopStat): number {
    const videos = record?.videos ?? [];
    return (videos.reduce((total, video) => total + video.value, 0) + (5 - videos.length) * missingTopValue(stat)) / 5;
}

export function topDisplayValue(value: number, level: MS_Level, stat: TopStat): number {
    return stat === 't' ? value / 1000 : stat === 's' ? value * STNB_COEFFICIENTS[level] : value;
}

export function formatTopValue(value: number, level: MS_Level, stat: TopStat): string {
    return stat === 't' ? ms_to_s(value) : topDisplayValue(value, level, stat).toFixed(3);
}

export function topRadius(value: number, anchor: number, stat: TopStat): number {
    if (anchor <= 0) return 0;
    if (stat === 't') return 100 * anchor / (value > 0 ? value : missingTopValue('t'));
    return 100 * (stat === 's' ? (value / anchor) ** (1 / 1.7) : value / anchor);
}

export function topEquivalentEt(value: number, anchors: TopAnchors, baseline = 1, nf = false): number | null {
    const anchor = anchors[topField(nf, 'e', 't')]?.value;
    if (anchor === undefined || anchor <= 0) return null;
    return value === 0 ? Infinity : anchor * baseline / (1000 * value);
}

export function topGrade(value: number, anchors: TopAnchors, baseline = 1, nf = false): { index: number; position: number } | null {
    const anchor = anchors[topField(nf, 'e', 't')]?.value;
    if (anchor === undefined || anchor <= 0) return null;
    const strength = value * 1000 / (baseline * anchor);
    let index = 0;
    // Keep exact boundaries in the stronger tier despite floating-point roundoff.
    while (index < 8 && strength + Number.EPSILON * strength >= gradeNodes[index + 1]) index++;
    return { index, position: Math.max(0, (strength - gradeNodes[index]) * gradeInverseWidths[index]) };
}

export function topSoftValues(records: TopRecords, anchors: TopAnchors): Record<SoftField, number> {
    const values = Object.fromEntries(softFields.map((field) => [field, 0])) as Record<SoftField, number>;
    for (const nf of [false, true]) {
        const mode = nf ? 'nf' : 'std';
        for (const level of topLevels) {
            const key = `${mode}:${level}` as SoftField;
            values[key] = topStats.reduce((total, stat) => {
                const field = topField(nf, level, stat);
                return total + softWeights[level][stat] * topRadius(topMean(records[field], stat), anchors[field]?.value ?? 0, stat) / 100;
            }, 0);
            values[`${mode}:sum`] += levelWeights[level] * values[key];
        }
    }
    values.lsf = values['std:sum'] * 0.97 + values['nf:sum'] * 0.03;
    return values;
}

export async function fetchSoftRanking(ranking: SoftField, start: number, end: number, signal?: AbortSignal): Promise<SoftRankingResult> {
    const { data } = await $axios.get<SoftRankingResult>('/api/speedranking/top/soft/rank', { params: { ranking, start, end }, signal });
    return data;
}

export async function fetchTopRanking(level: MS_Level, stat: TopStat, nf: boolean, start: number, end: number, signal?: AbortSignal): Promise<{ count: number; players: TopRankingPlayer[] }> {
    const { data } = await $axios.get<{ count: number; players: TopRankingPlayer[] }>('/api/speedranking/top/rank', { params: { level, stat, nf, start, end }, signal });
    return data;
}

export async function fetchTopPlayerRecords(playerId: number, signal?: AbortSignal): Promise<TopRecords> {
    const { data } = await $axios.get<TopRecords>(`/api/speedranking/top/player/${playerId}`, { signal });
    return data;
}
