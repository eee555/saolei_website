import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import type { PlayerMedals } from './medalService';

const { axiosGet, axiosPut } = vi.hoisted(() => ({ axiosGet: vi.fn(), axiosPut: vi.fn() }));
vi.mock('@/http', () => ({ default: { get: axiosGet, put: axiosPut } }));

function summary(scanPending = false, score = 0): PlayerMedals {
    return { scan_pending: scanPending, score, max_pins: 6, pin_ids: [], pins: [], series: [] };
}

function deferred() {
    let resolve!: (value: { data: PlayerMedals }) => void;
    let reject!: (reason: Error) => void;
    const promise = new Promise<{ data: PlayerMedals }>((resolvePromise, rejectPromise) => {
        resolve = resolvePromise;
        reject = rejectPromise;
    });
    return { promise, resolve, reject };
}

describe('shared medal image parts', () => {
    it('reuses one gold base and draws the number in the page', async () => {
        const { medalArtPlate, medalArtUrl } = await import('./medalService');
        expect(medalArtUrl('神速', 'ability.bvs.e', 50000)).toBe('/assets/medals/speed.webp?v=5');
        expect(medalArtUrl('神速', 'ability.bvs.b', 15000)).toBe('/assets/medals/speed.webp?v=5');
        expect(medalArtPlate('神速', 50000)).toBe('5');
        expect(medalArtPlate('神速', 15000)).toBe('1.5');
        expect(medalArtPlate('破境', 20000)).toBe('20');
        expect(medalArtPlate('实名在册', 1)).toBe('');
        expect(medalArtPlate('原始股东', 1000)).toBe('');
        expect(medalArtUrl('实名在册', 'novice.realname', 1)).toBe('/assets/medals/registered.webp?v=5');
        expect(medalArtUrl('原始股东', 'shareholder.origin', 1000)).toBe('/assets/medals/shareholder.webp?v=5');
        expect(medalArtUrl('神速', 'ability.bvs.e', null)).toBeUndefined();
        expect(medalArtUrl('unknown', 'unknown', 1)).toBeUndefined();
    });
});

describe('shared player medal summaries', () => {
    beforeEach(() => {
        vi.useFakeTimers();
        vi.resetModules();
        axiosGet.mockReset();
        axiosPut.mockReset();
    });
    afterEach(() => {
        vi.clearAllTimers();
        vi.useRealTimers();
    });

    it('shares inflight requests and cached summaries across sidebar and page', async () => {
        const { subscribePlayerMedals, fetchPlayerMedals } = await import('./medalService');
        const pending = deferred();
        axiosGet.mockReturnValue(pending.promise);
        const sidebar = vi.fn<() => void>();
        const page = vi.fn<() => void>();
        const stopSidebar = subscribePlayerMedals(1, sidebar, vi.fn<() => void>());
        const stopPage = subscribePlayerMedals(1, page, vi.fn<() => void>());
        expect(axiosGet).toHaveBeenCalledTimes(1);
        const data = summary();
        pending.resolve({ data });
        await fetchPlayerMedals(1);
        expect(sidebar).toHaveBeenLastCalledWith(data);
        expect(page).toHaveBeenLastCalledWith(data);
        stopPage();
        subscribePlayerMedals(1, page, vi.fn<() => void>());
        expect(axiosGet).toHaveBeenCalledTimes(1);
        stopSidebar();
    });

    it.each(['resolve', 'reject'] as const)('ignores late %s after changing players', async (outcome) => {
        const { subscribePlayerMedals, fetchPlayerMedals } = await import('./medalService');
        const old = deferred();
        axiosGet.mockReturnValueOnce(old.promise).mockResolvedValueOnce({ data: summary(false, 2) });
        const receive = vi.fn<() => void>();
        const failed = vi.fn<() => void>();
        const stop = subscribePlayerMedals(1, receive, failed);
        stop();
        subscribePlayerMedals(2, receive, failed);
        await fetchPlayerMedals(2);
        const oldRequest = fetchPlayerMedals(1).catch(() => undefined);
        if (outcome === 'resolve') old.resolve({ data: summary(false, 1) });
        else old.reject(new Error('old request failed'));
        await oldRequest;
        expect(receive).toHaveBeenCalledTimes(1);
        expect(receive).toHaveBeenLastCalledWith(summary(false, 2));
        expect(failed).not.toHaveBeenCalled();
    });

    it('polls once per player and publishes the completed scan to all subscribers', async () => {
        const { subscribePlayerMedals, fetchPlayerMedals } = await import('./medalService');
        axiosGet.mockResolvedValueOnce({ data: summary(true) }).mockResolvedValue({ data: summary(false, 10) });
        const sidebar = vi.fn<() => void>();
        const page = vi.fn<() => void>();
        subscribePlayerMedals(1, sidebar, vi.fn<() => void>());
        subscribePlayerMedals(1, page, vi.fn<() => void>());
        await fetchPlayerMedals(1);
        await vi.advanceTimersByTimeAsync(2000);
        expect(axiosGet).toHaveBeenCalledTimes(2);
        expect(sidebar).toHaveBeenLastCalledWith(summary(false, 10));
        expect(page).toHaveBeenLastCalledWith(summary(false, 10));
        await vi.advanceTimersByTimeAsync(60_000);
        expect(axiosGet).toHaveBeenCalledTimes(2);
    });

    it('caps pending scans at ten retries and permits an explicit retry', async () => {
        const { subscribePlayerMedals, fetchPlayerMedals, refreshPlayerMedals } = await import('./medalService');
        axiosGet.mockResolvedValue({ data: summary(true) });
        subscribePlayerMedals(1, vi.fn<() => void>(), vi.fn<() => void>());
        await fetchPlayerMedals(1);
        await vi.advanceTimersByTimeAsync(60_000);
        expect(axiosGet).toHaveBeenCalledTimes(11);
        refreshPlayerMedals(1);
        await fetchPlayerMedals(1);
        expect(axiosGet).toHaveBeenCalledTimes(12);
    });

    it('stops polling when the last subscriber leaves, including an inflight response', async () => {
        const { subscribePlayerMedals, fetchPlayerMedals } = await import('./medalService');
        const pending = deferred();
        axiosGet.mockReturnValue(pending.promise);
        const receive = vi.fn<() => void>();
        const stop = subscribePlayerMedals(1, receive, vi.fn<() => void>());
        stop();
        pending.resolve({ data: summary(true) });
        await fetchPlayerMedals(1);
        await vi.advanceTimersByTimeAsync(60_000);
        expect(axiosGet).toHaveBeenCalledTimes(1);
        expect(receive).not.toHaveBeenCalled();
        const stopAgain = subscribePlayerMedals(1, receive, vi.fn<() => void>());
        await fetchPlayerMedals(1);
        stopAgain();
        await vi.advanceTimersByTimeAsync(60_000);
        expect(axiosGet).toHaveBeenCalledTimes(2);
    });

    it('refreshes expired cached summaries when a viewer returns', async () => {
        const { subscribePlayerMedals, fetchPlayerMedals } = await import('./medalService');
        axiosGet.mockResolvedValue({ data: summary() });
        const stop = subscribePlayerMedals(1, vi.fn<() => void>(), vi.fn<() => void>());
        await fetchPlayerMedals(1);
        stop();
        await vi.advanceTimersByTimeAsync(30_001);
        subscribePlayerMedals(1, vi.fn<() => void>(), vi.fn<() => void>());
        await fetchPlayerMedals(1);
        expect(axiosGet).toHaveBeenCalledTimes(2);
    });

    it('invalidates on saving pins and rejects stale responses from before the save', async () => {
        const { subscribePlayerMedals, fetchPlayerMedals, saveMedalPins } = await import('./medalService');
        const old = deferred();
        axiosGet.mockReturnValueOnce(old.promise).mockResolvedValue({ data: summary(false, 2) });
        axiosPut.mockResolvedValue({});
        const receive = vi.fn<() => void>();
        subscribePlayerMedals(1, receive, vi.fn<() => void>());
        const oldRequest = fetchPlayerMedals(1);
        await saveMedalPins([], 1);
        await fetchPlayerMedals(1);
        old.resolve({ data: summary(false, 1) });
        await oldRequest;
        expect(receive).toHaveBeenCalledTimes(1);
        expect(receive).toHaveBeenLastCalledWith(summary(false, 2));
        expect(await fetchPlayerMedals(1)).toEqual(summary(false, 2));
    });

    it('bounds retries after scan polling fails and keeps the last summary', async () => {
        const { subscribePlayerMedals, fetchPlayerMedals } = await import('./medalService');
        axiosGet.mockResolvedValueOnce({ data: summary(true) }).mockRejectedValue(new Error('offline'));
        const receive = vi.fn<() => void>();
        const failed = vi.fn<() => void>();
        subscribePlayerMedals(1, receive, failed);
        await fetchPlayerMedals(1);
        await vi.advanceTimersByTimeAsync(60_000);
        expect(axiosGet).toHaveBeenCalledTimes(11);
        expect(receive).toHaveBeenCalledTimes(1);
        expect(failed).toHaveBeenCalledTimes(10);
    });

    it('only refreshes the player whose pins were saved', async () => {
        const { subscribePlayerMedals, fetchPlayerMedals, saveMedalPins } = await import('./medalService');
        axiosGet.mockResolvedValue({ data: summary() });
        axiosPut.mockResolvedValue({});
        subscribePlayerMedals(1, vi.fn<() => void>(), vi.fn<() => void>());
        subscribePlayerMedals(2, vi.fn<() => void>(), vi.fn<() => void>());
        await Promise.all([fetchPlayerMedals(1), fetchPlayerMedals(2)]);
        await saveMedalPins([], 1);
        await fetchPlayerMedals(1);
        expect(axiosGet).toHaveBeenCalledTimes(3);
        expect(axiosGet).toHaveBeenLastCalledWith('/api/medal/players/1');
    });
});
