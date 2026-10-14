import { describe, expect, it } from 'vitest';

import { fullYear } from './datetime';
import { calculateTournamentScoreCurrent, decodeGSCBest, decodeWeeklyClassicBest, tournamentScoreDecayFactor } from './tournamentUser';

describe('TournamentUser best decoders', () => {
    it('decodes gsc best into score and order', () => {
        expect(decodeGSCBest(123456007)).toEqual({
            score: 123456,
            order: 7,
        });
    });

    it('decodes weekly classic best into score, year, and week', () => {
        expect(decodeWeeklyClassicBest(34567802612)).toEqual({
            score: 345678,
            year: 2026,
            week: 12,
        });
    });

    it('does not decode unsafe sentinel integers', () => {
        expect(decodeGSCBest(Number.MAX_SAFE_INTEGER + 1)).toBeUndefined();
        expect(decodeWeeklyClassicBest(Number.MAX_SAFE_INTEGER + 1)).toBeUndefined();
    });
});

describe('TournamentUser score decay', () => {
    it('uses a two-year half-life', () => {
        const lastUpdated = new Date('2026-01-01T00:00:00Z');
        const now = new Date(lastUpdated.getTime() + fullYear * 2);

        expect(tournamentScoreDecayFactor(lastUpdated, now)).toBeCloseTo(0.5);
        expect(calculateTournamentScoreCurrent(100, lastUpdated, now)).toBeCloseTo(50);
    });

    it('does not increase score for non-forward time', () => {
        expect(tournamentScoreDecayFactor('2026-01-02T00:00:00Z', '2026-01-01T00:00:00Z')).toBe(1);
    });
});
