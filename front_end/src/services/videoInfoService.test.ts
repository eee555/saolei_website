import 'fake-indexeddb/auto';

import { afterAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { nextTick } from 'vue';

import { getDatabase, VIDEO_INFO_STORE_NAME } from './database';
import { serviceConfig } from './store';
import { clearUnpublishedVideoCache, fetchVideoInfo, fetchVideoInfos, setVideoInfoViewer, videoDisplayFields, videoInfoDownloads } from './videoInfoService';
import type { ParsedVideoInfo } from './videoInfoService';

const { get } = vi.hoisted(() => ({ get: vi.fn() }));
vi.mock('@/http', () => ({ default: { get } }));
vi.mock('./store', async () => {
    const { ref } = await import('vue');
    return { serviceConfig: ref({ videoInfoBatchSize: 100, videoInfoBatchDelay: 250, videoInfoCacheUnpublished: false }) };
});

const publicRow = (id: number) => ({ id, ongoing_tournament: false });
const privateRow = (id: number) => ({ id, ongoing_tournament: true });
let sessionRevision = 0;

function parsed(id: number): ParsedVideoInfo {
    return {
        id,
        software: 'e',
        level: 'b',
        mode: '00',
        end_time: null,
        file_size: 123,
        timems: 1000,
        bv: 4,
        left: 5,
        right: 0,
        double: 1,
        left_ce: 3,
        right_ce: 0,
        double_ce: 1,
        path: 20,
        pluck: null,
        flag: 0,
        op: 1,
        isl: 0,
        cell0: 1,
        cell1: 2,
        cell2: 0,
        cell3: 0,
        cell4: 0,
        cell5: 0,
        cell6: 0,
        cell7: 0,
        cell8: 0,
        identifier: 'fixture',
        tournament_identifier: [],
    };
}

beforeEach(async () => {
    vi.stubGlobal('window', { location: { pathname: '/', search: '', hash: '#/player/7/videos' } });
    get.mockReset();
    setVideoInfoViewer(7, ++sessionRevision);
    serviceConfig.value.videoInfoCacheUnpublished = false;
    serviceConfig.value.videoInfoBatchSize = 100;
    const db = await getDatabase();
    await db.clear(VIDEO_INFO_STORE_NAME);
    get.mockImplementation((_url: string, options: { params: { ids: string } }) => Promise.resolve({ data: options.params.ids.split(',').map((id) => ({ ...parsed(Number(id)), ongoing_tournament: false })) }));
});

afterAll(async () => {
    (await getDatabase()).close();
    vi.unstubAllGlobals();
});

describe('parsed video cache', () => {
    it('batches ID-only lookups and shares their complete in-flight requests', async () => {
        const first = fetchVideoInfo(2);
        const duplicate = fetchVideoInfo(2);
        const second = fetchVideoInfo(1);
        expect(duplicate).toBe(first);
        const videos = await Promise.all([first, second]);
        expect(videos.map((video) => video.id)).toEqual([2, 1]);
        expect(get.mock.calls).toEqual([['/api/video/info/batch', { params: { ids: '2,1' } }]]);
        expect(await fetchVideoInfo(2)).toEqual(parsed(2));
        expect(get).toHaveBeenCalledOnce();
    });

    it('bounds ID-only batches and lets available IDs load alongside a missing ID', async () => {
        serviceConfig.value.videoInfoBatchSize = 2;
        get.mockImplementation((_url: string, options: { params: { ids: string } }) => Promise.resolve({ data: options.params.ids.split(',').map(Number).filter((id) => id !== 404).map((id) => ({ ...parsed(id), ongoing_tournament: false })) }));
        const results = await Promise.allSettled([fetchVideoInfo(1), fetchVideoInfo(404), fetchVideoInfo(2)]);
        expect(results[0].status).toBe('fulfilled');
        expect(results[1]).toMatchObject({ status: 'rejected', reason: new Error('Video 404 is missing or unavailable.') });
        expect(results[2].status).toBe('fulfilled');
        expect(get.mock.calls).toEqual([
            ['/api/video/info/batch', { params: { ids: '1,404' } }],
            ['/api/video/info/batch', { params: { ids: '2' } }],
        ]);
    });

    it('rejects an ID-only private result from a previous session while allowing public lookups to finish', async () => {
        serviceConfig.value.videoInfoCacheUnpublished = true;
        const response = Promise.withResolvers<{ data: (ParsedVideoInfo & { ongoing_tournament: boolean })[] }>();
        get.mockImplementationOnce(() => response.promise);
        const completed = Promise.allSettled([fetchVideoInfo(3), fetchVideoInfo(4)]);
        await vi.waitFor(() => {
            expect(get).toHaveBeenCalledOnce();
        });
        setVideoInfoViewer(8, ++sessionRevision);
        response.resolve({ data: [{ ...parsed(3), ...privateRow(3) }, { ...parsed(4), ...publicRow(4) }] });
        const [privateResult, publicResult] = await completed;
        expect(privateResult).toMatchObject({ status: 'rejected', reason: new Error('Login session changed.') });
        expect(publicResult.status).toBe('fulfilled');
        expect(await (await getDatabase()).get(VIDEO_INFO_STORE_NAME, ['public', 3])).toBeUndefined();
        expect(await (await getDatabase()).get(VIDEO_INFO_STORE_NAME, ['user:7', 3])).toBeUndefined();
        expect(await (await getDatabase()).get(VIDEO_INFO_STORE_NAME, ['user:8', 3])).toBeUndefined();
    });

    it('allows retry after an ID-only download failure', async () => {
        get.mockRejectedValueOnce(new Error('network'));
        await expect(fetchVideoInfo(5)).rejects.toThrow('network');
        await expect(fetchVideoInfo(5)).resolves.toMatchObject({ id: 5 });
        expect(get.mock.calls).toHaveLength(2);
    });

    it('classifies ID-only private results before caching and only reads the current user scope', async () => {
        get.mockResolvedValue({ data: [{ ...parsed(3), ongoing_tournament: true }] });
        await fetchVideoInfo(3);
        await fetchVideoInfo(3);
        expect(get).toHaveBeenCalledTimes(2);
        expect(await (await getDatabase()).count(VIDEO_INFO_STORE_NAME)).toBe(0);
        serviceConfig.value.videoInfoCacheUnpublished = true;
        await fetchVideoInfo(3);
        expect(await fetchVideoInfo(3)).toEqual(parsed(3));
        expect(get).toHaveBeenCalledTimes(3);
        expect(await (await getDatabase()).get(VIDEO_INFO_STORE_NAME, ['public', 3])).toBeUndefined();
        expect(await (await getDatabase()).get(VIDEO_INFO_STORE_NAME, ['user:7', 3])).toMatchObject({ data: parsed(3) });
        setVideoInfoViewer(8, ++sessionRevision);
        get.mockResolvedValue({ data: [] });
        await expect(fetchVideoInfo(3)).rejects.toThrow('missing or unavailable');
        expect(get).toHaveBeenCalledTimes(4);
    });

    it('preserves zero-time and nullable generated-statistic semantics', () => {
        expect(videoDisplayFields({ ...parsed(1), timems: 0 })).toMatchObject({ bvs: 0, iqg: 0, stnb: 0 });
        expect(videoDisplayFields({ ...parsed(1), bv: null, left: null })).toMatchObject({ cl: null, bvs: null, ioe: null, stnb: null });
    });

    it('merges duplicate requests, preserves query order and restores generated fields', async () => {
        const first = fetchVideoInfos([publicRow(2), publicRow(1), publicRow(2)]);
        const second = fetchVideoInfos([publicRow(1)]);
        const [rows] = await Promise.all([first, second]);
        expect(rows.map((row) => row.id)).toEqual([2, 1, 2]);
        expect(get).toHaveBeenCalledOnce();
        expect(videoDisplayFields(rows[0])).toMatchObject({ cl: 6, ce: 4, bvs: 4, thrp: 1, file_size: 123 });
        expect(await fetchVideoInfos([publicRow(2)])).toHaveLength(1);
        expect(get).toHaveBeenCalledOnce();
        const db = await getDatabase();
        expect(await db.get(VIDEO_INFO_STORE_NAME, ['public', 2])).toEqual({ id: 2, scope: 'public', data: parsed(2) });
    });

    it.each(['before batch', 'during request'] as const)('keeps public video loading alive when automatic login finishes %s', async (stage) => {
        setVideoInfoViewer(0, ++sessionRevision);
        const response = Promise.withResolvers<{ data: (ParsedVideoInfo & { ongoing_tournament: boolean })[] }>();
        get.mockReturnValue(response.promise);
        const loading = fetchVideoInfos([publicRow(9)]);
        const completed = expect(loading).resolves.toMatchObject([{ id: 9, timems: 1000 }]);
        if (stage === 'during request') {
            await vi.waitFor(() => {
                expect(get).toHaveBeenCalledOnce();
            });
        }
        setVideoInfoViewer(7, ++sessionRevision);
        const afterLogin = expect(fetchVideoInfos([publicRow(9)])).resolves.toMatchObject([{ id: 9, timems: 1000 }]);
        response.resolve({ data: [{ ...parsed(9), ongoing_tournament: false }] });
        await Promise.all([completed, afterLogin]);
        expect(get).toHaveBeenCalledOnce();
        expect(await (await getDatabase()).get(VIDEO_INFO_STORE_NAME, ['public', 9])).toEqual({ id: 9, scope: 'public', data: parsed(9) });
    });

    it('fetches unpublished entries live by default and isolates opted-in entries by user', async () => {
        get.mockResolvedValue({ data: [{ ...parsed(3), ongoing_tournament: true }] });
        await fetchVideoInfos([privateRow(3)]);
        await fetchVideoInfos([privateRow(3)]);
        expect(get).toHaveBeenCalledTimes(2);
        serviceConfig.value.videoInfoCacheUnpublished = true;
        await fetchVideoInfos([privateRow(3)]);
        await fetchVideoInfos([privateRow(3)]);
        expect(get).toHaveBeenCalledTimes(3);
        setVideoInfoViewer(8, ++sessionRevision);
        await fetchVideoInfos([privateRow(3)]);
        expect(get).toHaveBeenCalledTimes(4);
        serviceConfig.value.videoInfoCacheUnpublished = false;
        await clearUnpublishedVideoCache();
        expect(await (await getDatabase()).get(VIDEO_INFO_STORE_NAME, ['user:8', 3])).toBeUndefined();
    });

    it('shows unique download progress across batches and releases it after failure', async () => {
        serviceConfig.value.videoInfoBatchSize = 1;
        get.mockImplementationOnce(() => Promise.resolve({ data: [{ ...parsed(1), ongoing_tournament: false }] }));
        get.mockRejectedValueOnce(new Error('network'));
        const loading = fetchVideoInfos([publicRow(1), publicRow(1), publicRow(2)]);
        const rejected = expect(loading).rejects.toThrow('network');
        await vi.waitFor(() => {
            expect(get).toHaveBeenCalledOnce();
        });
        await vi.waitFor(() => {
            expect([...videoInfoDownloads.value[0].items.values()]).toEqual([true, false]);
        });
        expect(videoInfoDownloads.value[0].page).toBe('/player/7/videos');
        await rejected;
        expect(videoInfoDownloads.value).toEqual([]);
        await fetchVideoInfos([publicRow(1), publicRow(2)]);
        expect(get.mock.calls.at(-1)?.[1]).toEqual({ params: { ids: '2' } });
    });

    it('returns downloaded data when writing to IndexedDB fails', async () => {
        const db = await getDatabase();
        vi.spyOn(db, 'transaction').mockImplementation(() => {
            throw new Error('quota');
        });
        try {
            expect(await fetchVideoInfos([publicRow(5)])).toHaveLength(1);
        } finally {
            vi.restoreAllMocks();
        }
    });

    it('does not persist an unpublished response after the user disables caching in flight', async () => {
        serviceConfig.value.videoInfoCacheUnpublished = true;
        const response = Promise.withResolvers<{ data: (ParsedVideoInfo & { ongoing_tournament: boolean })[] }>();
        get.mockReturnValue(response.promise);
        const loading = fetchVideoInfos([privateRow(6)]);
        await vi.waitFor(() => {
            expect(get).toHaveBeenCalledOnce();
        });
        serviceConfig.value.videoInfoCacheUnpublished = false;
        await nextTick();
        response.resolve({ data: [{ ...parsed(6), ongoing_tournament: true }] });
        await loading;
        expect(await (await getDatabase()).get(VIDEO_INFO_STORE_NAME, ['user:7', 6])).toBeUndefined();
    });

    it('rejects an old-session response without writing private data for the next user', async () => {
        serviceConfig.value.videoInfoCacheUnpublished = true;
        const response = Promise.withResolvers<{ data: (ParsedVideoInfo & { ongoing_tournament: boolean })[] }>();
        get.mockReturnValue(response.promise);
        const loading = fetchVideoInfos([privateRow(7)]);
        const rejected = expect(loading).rejects.toThrow('Login session changed');
        await vi.waitFor(() => {
            expect(get).toHaveBeenCalledOnce();
        });
        setVideoInfoViewer(8, ++sessionRevision);
        response.resolve({ data: [{ ...parsed(7), ongoing_tournament: true }] });
        await rejected;
        expect(await (await getDatabase()).count(VIDEO_INFO_STORE_NAME)).toBe(0);
        expect(videoInfoDownloads.value).toEqual([]);
    });
});
