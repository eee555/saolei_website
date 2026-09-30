import $axios from '@/http';
import { ms_to_s } from '@/utils';

export const speedStats = ['bt', 'bb', 'it', 'ib', 'et', 'eb', 'sumt', 'sumb'] as const;
export type SpeedStat = typeof speedStats[number];
export type SpeedBoard = 'saolei' | 'saolei_nf';
type SingleStat = Exclude<SpeedStat, 'sumt' | 'sumb'>;
export type SpeedRecord = Record<SpeedStat, number | null> & Record<`${SingleStat}_id`, number | null> & { player_id: number };

export function isTimeStat(stat: SpeedStat): boolean {
    return stat.endsWith('t');
}

export function formatSpeedValue(record: SpeedRecord | undefined, stat: SpeedStat): string {
    const value = record?.[stat];
    if (value == null) return '--';
    return isTimeStat(stat) ? ms_to_s(value) : value.toFixed(3);
}

export function speedVideoId(record: SpeedRecord | undefined, stat: SpeedStat): number | undefined {
    if (stat === 'sumt' || stat === 'sumb') return undefined;
    return record?.[`${stat}_id`] ?? undefined;
}

export async function fetchSpeedRanking(board: SpeedBoard, stat: SpeedStat, start: number, end: number): Promise<{ count: number; players: SpeedRecord[] }> {
    const { data } = await $axios.get<{ count: number; players: SpeedRecord[] }>('/api/speedranking/rank', {
        params: { board, stat, start, end },
    });
    return data;
}

export async function fetchSpeedRecord(playerId: number, board: SpeedBoard): Promise<SpeedRecord> {
    const { data } = await $axios.get<SpeedRecord>(`/api/speedranking/player/${playerId}`, { params: { board } });
    return data;
}
