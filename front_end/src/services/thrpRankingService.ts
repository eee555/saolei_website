import $axios from '@/http';

export const thrpLevels = ['b', 'i', 'e'] as const;
export type ThrpLevel = typeof thrpLevels[number];
export const thrpStats = [...thrpLevels, 'sum'] as const;
export type ThrpStat = typeof thrpStats[number];

export interface ThrpVideoRecord {
    value: number;
    video_id: number;
    upload_time: string;
}
export type ThrpRecord = { player_id: number } & Record<ThrpLevel, ThrpVideoRecord | null>;
export type ThrpPlayerRecord = ThrpRecord & { ranks: Record<ThrpStat, number | null> };

export function thrpValue(record: ThrpRecord, stat: ThrpStat): number | null {
    return stat === 'sum' ? thrpLevels.reduce((sum, level) => sum + (record[level]?.value ?? 0), 0) : record[stat]?.value ?? null;
}

export function thrpVideoId(record: ThrpRecord, stat: ThrpStat): number | undefined {
    return stat === 'sum' ? undefined : record[stat]?.video_id;
}

export async function fetchThrpRanking(stat: ThrpStat, start: number, end: number, signal?: AbortSignal): Promise<{ count: number; players: ThrpRecord[] }> {
    const { data } = await $axios.get<{ count: number; players: ThrpRecord[] }>('/api/effranking/thrp/rank', { params: { stat, start, end }, signal });
    return data;
}

export async function fetchThrpRecord(playerId: number): Promise<ThrpPlayerRecord> {
    const { data } = await $axios.get<ThrpPlayerRecord>(`/api/effranking/thrp/player/${playerId}`);
    return data;
}

export async function rebuildThrpRecord(playerId: number, stat: ThrpStat): Promise<ThrpRecord> {
    const { data } = await $axios.post<ThrpRecord>('/api/effranking/thrp/admin/rebuild_record', { player_id: playerId, stat });
    return data;
}
