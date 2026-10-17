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
    mean: number;
    videos: TopVideo[];
}
export interface TopAnchor {
    value: number;
    sample_count: number;
}
export type TopRecords = Partial<Record<TopField, TopRecord>>;
export type TopAnchors = Partial<Record<TopField, TopAnchor>>;

export function topField(nf: boolean, level: MS_Level, stat: TopStat): TopField {
    return `${nf ? 'nf' : 'std'}:${level}${stat}`;
}

export function missingTopValue(stat: TopStat): number {
    return stat === 't' ? 999999 : 0;
}

export function topDisplayValue(value: number, level: MS_Level, stat: TopStat): number {
    return stat === 't' ? value / 1000 : stat === 's' ? value * STNB_COEFFICIENTS[level] : value;
}

export function formatTopValue(value: number, level: MS_Level, stat: TopStat): string {
    return stat === 't' ? ms_to_s(value) : topDisplayValue(value, level, stat).toFixed(3);
}

export function topRadius(value: number, anchor: number, stat: TopStat): number {
    if (anchor <= 0) return 0;
    const denominator = stat === 't' ? value : anchor;
    return denominator > 0 ? 100 * (stat === 't' ? anchor : value) / denominator : 0;
}

export async function fetchTopRanking(level: MS_Level, stat: TopStat, nf: boolean, start: number, end: number, signal?: AbortSignal): Promise<{ count: number; players: TopRankingPlayer[] }> {
    const { data } = await $axios.get<{ count: number; players: TopRankingPlayer[] }>('/api/speedranking/top/rank', { params: { level, stat, nf, start, end }, signal });
    return data;
}

export async function fetchTopPlayerRecords(playerId: number, signal?: AbortSignal): Promise<TopRecords> {
    const { data } = await $axios.get<TopRecords>(`/api/speedranking/top/player/${playerId}`, { signal });
    return data;
}

export async function fetchTopAnchors(signal?: AbortSignal): Promise<TopAnchors> {
    const { data } = await $axios.get<TopAnchors>('/api/speedranking/top/anchors', { signal });
    return data;
}
