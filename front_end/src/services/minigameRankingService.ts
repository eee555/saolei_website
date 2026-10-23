import type { CSSProperties } from 'vue';

import $axios from '@/http';
import type { TrainingGame } from '@/utils/minigame/games';

export interface MinigameRanking {
    key: string;
    game: TrainingGame;
    level: 'b' | 'i' | 'e';
    density: '50' | '75' | '87.5' | null;
    order: 'asc' | 'desc';
    unit: 'ms';
    min_score: number;
    max_score: number;
    accept_submissions: boolean;
}

export interface MinigameScore {
    score: number;
    achieved_at: string;
}

export interface MinigameRankingRow {
    player_id: number;
    rank: number;
    records: Record<string, MinigameScore | null>;
}

export interface MinigameRankingGroup {
    game: TrainingGame;
    rankings: MinigameRanking[];
}

// Supply a scheme here when score colors have been defined for these games.
export type MinigameColorScheme = (ranking: MinigameRanking, score: number) => CSSProperties | undefined;

let definitions: Promise<MinigameRankingGroup[]> | undefined;

export function fetchMinigameRankings(): Promise<MinigameRankingGroup[]> {
    definitions ??= $axios.get<MinigameRankingGroup[]>('/api/minigame/rankings').then(({ data }) => data).catch((error: unknown) => {
        definitions = undefined;
        throw error;
    });
    return definitions;
}

export async function fetchMinigameRanking(game: TrainingGame, sort: string, start: number, end: number): Promise<{ count: number; players: MinigameRankingRow[] }> {
    const { data } = await $axios.get<{ count: number; players: MinigameRankingRow[] }>(`/api/minigame/${game}/rank`, { params: { sort, start, end } });
    return data;
}

export async function submitMinigameScore(rankingKey: string, score: number): Promise<{ improved: boolean; record: MinigameScore & { id: number; ranking_key: string; player_id: number } }> {
    const { data } = await $axios.post<{ improved: boolean; record: MinigameScore & { id: number; ranking_key: string; player_id: number } }>(`/api/minigame/${rankingKey}/score`, { score });
    return data;
}
