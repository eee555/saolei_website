import $axios from '@/http';
import { ms_to_s } from '@/utils';

export const SaoleiLevels = ['b', 'i', 'e'] as const;
export type SaoleiLevel = typeof SaoleiLevels[number];
export const SaoleiStat = {
    t: 'time',
    b: 'bvs',
} as const;
export type SaoleiStat = keyof typeof SaoleiStat;
export type SaoleiBoard = 'saolei' | 'saolei_nf';
export type SaoleiField = `${SaoleiLevel | 'sum'}${SaoleiStat}`;
export const saoleiFields = ['bt', 'bb', 'it', 'ib', 'et', 'eb', 'sumt', 'sumb'] as const satisfies readonly SaoleiField[];
export type SaoleiRecord = Record<SaoleiField, number | null> & Record<`${SaoleiLevel}${SaoleiStat}_id`, number | null> & { player_id: number };

export function isSaoleiTimeStat(stat: SaoleiField): boolean {
    return stat.endsWith('t');
}

export function formatSaoleiValue(record: SaoleiRecord | undefined, stat: SaoleiField): string {
    const value = record?.[stat];
    if (value == null) return '--';
    return isSaoleiTimeStat(stat) ? ms_to_s(value) : value.toFixed(3);
}

export function saoleiVideoId(record: SaoleiRecord | undefined, stat: SaoleiField): number | undefined {
    if (stat === 'sumt' || stat === 'sumb') return undefined;
    return record?.[`${stat}_id`] ?? undefined;
}

export async function fetchSaoleiRanking(board: SaoleiBoard, stat: SaoleiField, start: number, end: number): Promise<{ count: number; players: SaoleiRecord[] }> {
    const { data } = await $axios.get<{ count: number; players: SaoleiRecord[] }>('/api/speedranking/rank', {
        params: { board, stat, start, end },
    });
    return data;
}

export async function fetchSaoleiRecord(playerId: number, board: SaoleiBoard): Promise<SaoleiRecord> {
    const { data } = await $axios.get<SaoleiRecord>(`/api/speedranking/player/${playerId}`, { params: { board } });
    return data;
}
