import $axios from '@/http';
import type { TournamentInfo, TournamentParticipant } from '@/utils/tournaments';
import type { VideoAbstractData } from '@/utils/videoabstract';

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

export interface WeeklyScoreResponse {
    id: number;
    user_id: number | null;
    start_time: string;
    end_time: string | null;
    rank: number | null;
    rank_score: number;
    classic_et: [number, number][];
    classic_it: [number, number][];
    classic_score: number;
}

interface ParticipantVideosParams {
    userId: number;
    tournamentId: number;
}

export type TournamentListCategory = 'normal' | 'awarded' | 'other' | 'all';

export async function fetchTournamentList(category: TournamentListCategory = 'all'): Promise<TournamentInfo[]> {
    const { data } = await $axios.get<TournamentInfo[]>('/api/tournament/get_list', {
        params: { category },
    });
    return data;
}

export async function fetchTournament(tournamentId: number | string): Promise<TournamentInfo> {
    const { data } = await $axios.get<TournamentInfo>('/api/tournament/get', {
        params: { tournament_id: tournamentId },
    });
    return data;
}

export async function fetchParticipantList(tournamentId: number): Promise<TournamentParticipant[]> {
    const { data } = await $axios.get<TournamentParticipant[]>('/api/tournament/participants', {
        params: { tournament_id: tournamentId },
    });
    return data;
}

export async function fetchGSCResults(tournamentId: number): Promise<GSCParticipantResponse[]> {
    const { data } = await $axios.get<GSCParticipantResponse[]>('/api/tournament/gsc/results', {
        params: { tournament_id: tournamentId },
    });
    return data;
}

export async function fetchWeeklyResults(tournamentId: number): Promise<WeeklyScoreResponse[]> {
    const { data } = await $axios.get<WeeklyScoreResponse[]>('/api/tournament/weekly/results', {
        params: { tournament_id: tournamentId },
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
