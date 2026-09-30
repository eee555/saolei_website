import $axios from '@/http';
import { ms_to_s } from '@/utils';

export const saoleiStats = ['bt', 'bb', 'it', 'ib', 'et', 'eb', 'sumt', 'sumb'] as const;
export type SaoleiStat = typeof saoleiStats[number];
export type SaoleiBoard = 'saolei' | 'saolei_nf';
type SingleStat = Exclude<SaoleiStat, 'sumt' | 'sumb'>;
export type SaoleiRecord = Record<SaoleiStat, number | null> & Record<`${SingleStat}_id`, number | null> & { player_id: number };

export function isSaoleiTimeStat(stat: SaoleiStat): boolean {
    return stat.endsWith('t');
}

export function formatSaoleiValue(record: SaoleiRecord | undefined, stat: SaoleiStat): string {
    const value = record?.[stat];
    if (value == null) return '--';
    return isSaoleiTimeStat(stat) ? ms_to_s(value) : value.toFixed(3);
}

export function saoleiVideoId(record: SaoleiRecord | undefined, stat: SaoleiStat): number | undefined {
    if (stat === 'sumt' || stat === 'sumb') return undefined;
    return record?.[`${stat}_id`] ?? undefined;
}

export async function fetchSaoleiRanking(board: SaoleiBoard, stat: SaoleiStat, start: number, end: number): Promise<{ count: number; players: SaoleiRecord[] }> {
    const { data } = await $axios.get<{ count: number; players: SaoleiRecord[] }>('/api/speedranking/rank', {
        params: { board, stat, start, end },
    });
    return data;
}

export async function fetchSaoleiRecord(playerId: number, board: SaoleiBoard): Promise<SaoleiRecord> {
    const { data } = await $axios.get<SaoleiRecord>(`/api/speedranking/player/${playerId}`, { params: { board } });
    return data;
}
