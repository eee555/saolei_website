import $axios from '@/http';
import { GSCParticipant } from '@/utils/gsc';
import type { TournamentInfo } from '@/utils/tournaments';
import { TournamentParticipant } from '@/utils/tournaments';
import type { VideoAbstractData } from '@/utils/videoabstract';
import { WeeklyParticipant } from '@/utils/weekly';

export interface GSCParticipantResponse {
    id: number;
    user_id: number;
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
    user_id: number;
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
export const TournamentUserRankFields = [
    'score_current', 'score_total',
    'gsc_total', 'gsc_best',
    'weekly_total', 'weekly_classic_total', 'weekly_classic_best',
] as const;
export type TournamentUserRankField = typeof TournamentUserRankFields[number];

export interface TournamentUserRankingRow {
    user_id: number;
    score_current: number;
    last_updated: string;
    score_total: number;
    gsc_total: number;
    gsc_best: number;
    weekly_total: number;
    weekly_classic_total: number;
    weekly_classic_best: number;
}

export interface TournamentUserRankingResponse {
    total: number;
    data: TournamentUserRankingRow[];
}

interface TournamentUserRankingParams {
    sortBy: TournamentUserRankField;
    start: number;
    end: number;
}

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
    return data.map((value) => new TournamentParticipant(value));
}

export async function fetchTournamentUserRanking(params: TournamentUserRankingParams): Promise<TournamentUserRankingResponse> {
    const { data } = await $axios.get<TournamentUserRankingResponse>('/api/tournament/user-ranking', {
        params: {
            sort_by: params.sortBy,
            start: params.start,
            end: params.end,
        },
    });
    return data;
}

export async function fetchGSCResults(tournamentId: number): Promise<GSCParticipant[]> {
    const { data } = await $axios.get<GSCParticipantResponse[]>('/api/tournament/gsc/results', {
        params: { tournament_id: tournamentId },
    });
    return data.map((value) => new GSCParticipant(value));
}

export async function fetchWeeklyResults(tournamentId: number): Promise<WeeklyParticipant[]> {
    const { data } = await $axios.get<WeeklyScoreResponse[]>('/api/tournament/weekly/results', {
        params: { tournament_id: tournamentId },
    });
    return data.map((value) => new WeeklyParticipant(value));
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

export async function fetchTournamentVideos(tournamentId: number): Promise<VideoAbstractData[]> {
    const { data } = await $axios.get<VideoAbstractData[]>('/api/tournament/get_videos/tournament', {
        params: { tournament_id: tournamentId },
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
