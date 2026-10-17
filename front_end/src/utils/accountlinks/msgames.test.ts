import { describe, expect, it } from 'vitest';

import { canImportMSGamesVideo } from './msgames';

const normal = { filename: 'example.avf', category: 'Time / beginner / NF / Official', score: 'Time: 0.490; 3BV: 3' };
const density = (board: string, score: string) => ({ ...normal, category: `Density / ${board} / NF / Official`, score });

describe('canImportMSGamesVideo', () => {
    it('allows supported formats and rejects unsupported formats including Density replays', () => {
        for (const filename of ['example.avf', 'example.MVF', 'example.rmv']) {
            expect(canImportMSGamesVideo({ ...normal, filename })).toBe(true);
        }
        for (const filename of ['legacy.mvr', 'example.evf', 'no-extension']) {
            expect(canImportMSGamesVideo({ ...normal, filename })).toBe(false);
            expect(canImportMSGamesVideo({ ...density('8x8', 'Density: Mines: 40'), filename })).toBe(false);
        }
    });

    it('accepts all four Density configurations using columns by rows from MSGames', () => {
        for (const [board, mines] of [['8x8', 40], ['16x16', 100], ['30x16', 150], ['30x24', 200]] as const) {
            expect(canImportMSGamesVideo(density(board, `Density: Time: 20.000; 3BV: 10; Mines: ${mines}`))).toBe(true);
        }
    });

    it('rejects unknown, missing or conflicting Density board and mine information', () => {
        for (const value of [
            density('9x9', 'Density: Mines: 40'), density('8x8', 'Density: Mines: 41'),
            density('', 'Density: Mines: 40'), density('unknown', 'Density: Mines: 40'),
            density('8x8, 9x9', 'Density: Mines: 40'), density('8x8', 'Time: 20.000'),
            density('8x8', 'Density: Time: 20.000'), density('8x8', 'Density: Mines: -'),
            density('8x8', 'Density: Mines: 40.5'), density('8x8', 'Density: Mines: 40\nDensity: Mines: 41'),
        ]) expect(canImportMSGamesVideo(value)).toBe(false);
    });

    it('checks Density restrictions when one URL is also listed under other metrics', () => {
        const category = 'Time / beginner / NF\nDensity / 8x8 / NF';
        expect(canImportMSGamesVideo({ ...normal, category, score: 'Time: 20.000\nDensity: Mines: 40' })).toBe(true);
        expect(canImportMSGamesVideo({ ...normal, category, score: 'Time: 20.000\nDensity: Mines: 41' })).toBe(false);
    });
});
