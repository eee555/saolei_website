import $axios from '@/http';

type RecordId = number | null;

export type UserRecordLevel = 'b' | 'e' | 'i';
export type UserRecordMode = 'dg' | 'nf' | 'ng' | 'std';
export type UserRecordStat = 'bvs' | 'ioe' | 'path' | 'stnb' | 'timems';
export type UserRecordsAbstractStat = Extract<UserRecordStat, 'bvs' | 'timems'>;
type UserRecordValueField = `${UserRecordLevel}_${UserRecordStat}_${UserRecordMode}`;
type UserRecordIdField = `${UserRecordLevel}_${UserRecordStat}_id_${UserRecordMode}`;
type UserRecordAbstractValueField = `${UserRecordLevel}_${UserRecordsAbstractStat}_std`;
type UserRecordAbstractIdField = `${UserRecordLevel}_${UserRecordsAbstractStat}_id_std`;
export type UserRecordsResponse = Record<UserRecordValueField, number> & Record<UserRecordIdField, number | null>;
export type UserRecordsAbstractResponse
    = Record<UserRecordAbstractValueField, number> & Record<UserRecordAbstractIdField, RecordId>;

export interface CustomPluckRecord {
    level: string;
    video_id: number;
    pluck: number;
}

type PlayerRankValue = number | string;

export interface PlayerRankResponse {
    total_page: number;
    players: PlayerRankValue[];
}

export interface FetchPlayerRankParams {
    ids: string;
    sortBy: string;
    reverse: boolean;
    indexes: string;
    page: number;
}

export async function fetchPlayerRecordsAbstract(userId: number): Promise<UserRecordsAbstractResponse> {
    const { data } = await $axios.get<UserRecordsAbstractResponse>('/api/msuser/records_abstract', {
        params: { id: userId },
    });
    return data;
}

export async function fetchUserRecords(userId: number): Promise<UserRecordsResponse> {
    const { data } = await $axios.get<UserRecordsResponse>('/api/msuser/records', {
        params: { id: userId },
    });
    return data;
}

export async function fetchCustomPluckPlayerRecords(userId: number): Promise<CustomPluckRecord[]> {
    const { data } = await $axios.get<CustomPluckRecord[]>('/api/customranking/pluck/player', {
        params: { player_id: userId },
    });
    return data;
}

export async function fetchPlayerRank(params: FetchPlayerRankParams): Promise<PlayerRankResponse> {
    const { data } = await $axios.get<PlayerRankResponse>('/msuser/player_rank/', {
        params: {
            ids: params.ids,
            sort_by: params.sortBy,
            reverse: params.reverse,
            indexes: params.indexes,
            page: params.page,
        },
    });
    return data;
}
