import $axios from '@/http';
import type { RecordBIE } from '@/utils/common/structInterface';

type RecordId = number | null;

export interface PlayerRecordAbstract {
    timems: number[];
    timems_id: RecordId[];
    bvs: number[];
    bvs_id: RecordId[];
}

interface PlayerRecordAbstractResponse {
    record_abstract: string;
}

interface UserRecordsSuccessResponse {
    id: string;
    std_record: string;
    nf_record: string;
    ng_record: string;
    dg_record: string;
}

interface UserRecordsErrorResponse {
    status: number;
    msg?: string;
}

type UserRecordsResponse = UserRecordsSuccessResponse | UserRecordsErrorResponse;

export type UserRecordsResult
    = {
        type: 'success';
        records: RecordBIE[];
    }
    | {
        type: 'error';
        status: number;
        msg?: string;
    };

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

export async function fetchPlayerRecordAbstract(userId: number): Promise<PlayerRecordAbstract> {
    const { data } = await $axios.get<PlayerRecordAbstractResponse>('/msuser/info_abstract/', {
        params: { id: userId },
    });
    return JSON.parse(data.record_abstract) as PlayerRecordAbstract;
}

export async function fetchUserRecords(userId: number): Promise<UserRecordsResult> {
    const { data } = await $axios.get<UserRecordsResponse>('/msuser/records/', {
        params: { id: userId },
    });

    if (!('std_record' in data)) {
        return {
            type: 'error',
            status: data.status,
            msg: data.msg,
        };
    }

    return {
        type: 'success',
        records: [
            parseRecord(data.std_record),
            parseRecord(data.nf_record),
            parseRecord(data.ng_record),
            parseRecord(data.dg_record),
        ],
    };
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

function parseRecord(record: string): RecordBIE {
    return JSON.parse(record) as RecordBIE;
}
