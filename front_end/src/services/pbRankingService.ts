import $axios from '@/http';
import { ms_to_s } from '@/utils';
import { toISODateTimeString } from '@/utils/datetime';
import type { MS_Level } from '@/utils/ms_const';

export interface PBRankingPlayer {
    player_id: number;
    video_id: number;
    timems: number;
    upload_time: string;
}

export type PBStat = 'time' | 'bvs' | 'stnb';
export const pbStats = ['time', 'bvs', 'stnb'] as const;
export const pbLevels = ['b', 'i', 'e'] as const;
export const pbBVLimits = { b: { min: 1, max: 54 }, i: { min: 1, max: 216 }, e: { min: 1, max: 381 } } as const;
export type PBCounts = Partial<Record<`${'std' | 'nf'}:${MS_Level}:${number}`, number>>;
const stnbCoefficients = { b: 36, i: 162, e: 435 } as const;

export function formatPBValue(timems: number, level: MS_Level, bv: number, stat: PBStat): string {
    if (stat === 'time') return ms_to_s(timems);
    const seconds = timems / 1000;
    return (stat === 'bvs' ? bv / seconds : stnbCoefficients[level] * bv / seconds ** 1.7).toFixed(3);
}

export function formatPBUploadTime(value: string): string {
    return toISODateTimeString(new Date(value)).slice(0, 16);
}

export async function fetchPBCounts(): Promise<PBCounts> {
    const { data } = await $axios.get<PBCounts>('/api/speedranking/pb/counts');
    return data;
}

export async function fetchPBRanking(level: MS_Level, bv: number, nf: boolean, start: number, end: number): Promise<{ count: number; players: PBRankingPlayer[] }> {
    const { data } = await $axios.get<{ count: number; players: PBRankingPlayer[] }>('/api/speedranking/pb/rank', {
        params: { level, bv, nf, start, end },
    });
    return data;
}
