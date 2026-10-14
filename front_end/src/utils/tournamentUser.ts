import { fullYear } from './datetime';

export interface GSCBest {
    score: number;
    order: number;
}

export interface WeeklyClassicBest {
    score: number;
    year: number;
    week: number;
}

const TOURNAMENT_SCORE_HALF_LIFE_MS = fullYear * 2;

export function tournamentScoreDecayFactor(lastUpdated: Date | string | number, now: Date | string | number): number {
    const lastUpdatedTime = new Date(lastUpdated).getTime();
    const nowTime = new Date(now).getTime();
    if (nowTime <= lastUpdatedTime) return 1;
    return 1 / 2 ** ((nowTime - lastUpdatedTime) / TOURNAMENT_SCORE_HALF_LIFE_MS);
}

export function calculateTournamentScoreCurrent(scoreCurrent: number, lastUpdated: Date | string | number, now: Date | string | number): number {
    return scoreCurrent * tournamentScoreDecayFactor(lastUpdated, now);
}

export function decodeGSCBest(value: number): GSCBest | undefined {
    if (!Number.isSafeInteger(value)) return undefined;
    return {
        score: Math.floor(value / 1000),
        order: value % 1000,
    };
}

export function decodeWeeklyClassicBest(value: number): WeeklyClassicBest | undefined {
    if (!Number.isSafeInteger(value)) return undefined;
    const tournament = value % 100000;
    return {
        score: Math.floor(value / 100000),
        year: 2000 + Math.floor(tournament / 100),
        week: tournament % 100,
    };
}
