import $axios from '@/http';
import type { TournamentInfo } from '@/utils/tournaments';
import type { VideoAbstractData } from '@/utils/videoabstract';

export interface GSCTournamentInfo extends TournamentInfo {
    order: number;
    token: string;
}

export interface GSCParticipantResponse {
    id: number;
    user__id: number;
    user__realname: string;
    rank: number | null;
    rank_score: number;
    bt1st: number;
    bt20th: number;
    bt20sum: number;
    it1st: number;
    it12th: number;
    it12sum: number;
    et1st: number;
    et5th: number;
    et5sum: number;
    t37?: number;
}

export interface GSCInfoResponse {
    data: GSCTournamentInfo;
    results: GSCParticipantResponse[] | null;
    participant: boolean;
    identifier: string | null;
}

interface ParticipantVideosParams {
    userId: number;
    tournamentId: number;
}

export async function fetchTournamentList(): Promise<TournamentInfo[]> {
    const { data } = await $axios.get<TournamentInfo[]>('/api/tournament/get_list');
    return data;
}

export async function fetchTournament(tournamentId: number | string): Promise<TournamentInfo> {
    const { data } = await $axios.get<TournamentInfo>('/api/tournament/get', {
        params: { id: tournamentId },
    });
    return data;
}

export async function fetchGSCInfo(tournamentId: number): Promise<GSCInfoResponse> {
    const { data } = await $axios.get<GSCInfoResponse>('/api/tournament/gsc/info', {
        params: { id: tournamentId },
    });
    return data;
}

export async function fetchParticipantVideos(params: ParticipantVideosParams): Promise<VideoAbstractData[]> {
    const { data } = await $axios.get<VideoAbstractData[]>('/api/tournament/get_videos/participant', {
        params: {
            user_id: params.userId,
            tournament_id: params.tournamentId,
        },
    });
    return data;
}

export async function downloadTournamentVideos(tournamentId: number): Promise<ArrayBuffer> {
    const { data } = await $axios.get<ArrayBuffer>('/api/tournament/download', {
        params: { tournament_id: tournamentId },
        responseType: 'arraybuffer',
    });
    return data;
}

export async function downloadParticipantTournamentVideos(params: ParticipantVideosParams): Promise<ArrayBuffer> {
    const { data } = await $axios.get<ArrayBuffer>('/api/tournament/download/participant', {
        params: {
            user_id: params.userId,
            tournament_id: params.tournamentId,
        },
        responseType: 'arraybuffer',
    });
    return data;
}
