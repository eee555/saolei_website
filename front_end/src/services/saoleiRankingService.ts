import $axios from '@/http';
import { ms_to_s } from '@/utils';

export const SaoleiLevels = ['b', 'i', 'e'] as const;
export type SaoleiLevel = typeof SaoleiLevels[number];
export const SaoleiStat = {
    t: 'time',
    b: 'bvs',
} as const;
export type SaoleiStat = keyof typeof SaoleiStat;
export type SaoleiRankingName = 'saolei' | 'saolei_nf';
export type SaoleiField = `${SaoleiLevel | 'sum'}${SaoleiStat}`;
export const saoleiFields = ['bt', 'bb', 'it', 'ib', 'et', 'eb', 'sumt', 'sumb'] as const satisfies readonly SaoleiField[];
export type SaoleiRecord = Record<SaoleiField, number | null> & Record<`${SaoleiLevel}${SaoleiStat}_id`, number | null> & { player_id: number };
export type SaoleiPlayerRecord = SaoleiRecord & { ranks: Record<SaoleiField, number | null> };

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

export async function fetchSaoleiRanking(rankingName: SaoleiRankingName, stat: SaoleiField, start: number, end: number): Promise<{ count: number; players: SaoleiRecord[] }> {
    const { data } = await $axios.get<{ count: number; players: SaoleiRecord[] }>('/api/speedranking/rank', {
        params: { ranking_name: rankingName, stat, start, end },
    });
    return data;
}

export async function fetchSaoleiRecords(playerId: number): Promise<Record<SaoleiRankingName, SaoleiPlayerRecord>> {
    const { data } = await $axios.get<Record<SaoleiRankingName, SaoleiPlayerRecord>>(`/api/speedranking/player/${playerId}`);
    return data;
}
