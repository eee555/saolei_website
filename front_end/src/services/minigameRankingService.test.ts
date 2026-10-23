import { afterEach, describe, expect, it, vi } from 'vitest';

import { fetchMinigameRankings } from './minigameRankingService';

import $axios from '@/http';

describe('minigame ranking API', () => {
    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('shares ranking metadata requests and retries after a failure', async () => {
        const get = vi.spyOn($axios, 'get').mockRejectedValueOnce(new Error('offline')).mockResolvedValue({ data: [{ game: 'flag-chord', rankings: [] }] });
        await expect(fetchMinigameRankings()).rejects.toThrow('offline');
        const [first, second] = await Promise.all([fetchMinigameRankings(), fetchMinigameRankings()]);
        expect(first).toBe(second);
        expect(get).toHaveBeenCalledTimes(2);
        expect(get).toHaveBeenLastCalledWith('/api/minigame/rankings');
    });
});
