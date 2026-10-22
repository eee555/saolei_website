import { AxiosError, AxiosHeaders } from 'axios';
import type { AxiosInstance, AxiosResponse } from 'axios';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { effectScope, ref } from 'vue';
import type { EffectScope } from 'vue';

import { useSiteReplayInfo } from './useSiteReplayInfo';
import type { SiteReplayInfo } from './useSiteReplayInfo';

const { get } = vi.hoisted(() => ({ get: vi.fn<AxiosInstance['get']>() }));
vi.mock('@/http', () => ({ default: { get } }));
vi.mock('@/services/videoInfoService', () => ({
    fetchVideoInfos: (rows: Record<string, unknown>[]) => Promise.resolve(rows.map((row) => ({ ...row, identifier: 'Fixture', tournament_identifier: [] }))),
    videoDisplayFields: (row: Record<string, unknown>) => row,
}));
const scopes: EffectScope[] = [];
function data(id = 42): SiteReplayInfo {
    const video = { id, player: 7, upload_time: '2026-10-12T10:00:00Z', state: 'c', ongoing_tournament: false, identifier: 'Fixture', tournament_identifier: [] };
    return { video, expanded_video: { identifier: 'Fixture', tournament_identifier: [] }, tournament_ids: [2, 3], filename: 'original.evf', rankings: [] };
}
function response(info: SiteReplayInfo): AxiosResponse<Omit<SiteReplayInfo, 'expanded_video'>> {
    const wire = {
        video: { id: info.video.id, player: info.video.player, upload_time: info.video.upload_time, state: 'c', ongoing_tournament: false },
        tournament_ids: info.tournament_ids,
        filename: info.filename,
        rankings: info.rankings,
    };
    return { data: wire, status: 200, statusText: 'OK', headers: {}, config: { headers: new AxiosHeaders() } };
}
function setup() {
    const id = ref('42');
    const scope = effectScope();
    scopes.push(scope);
    const state = scope.run(() => useSiteReplayInfo(id));
    if (!state) throw new Error('Expected info scope');
    return { id, scope, ...state };
}
afterEach(() => {
    for (const scope of scopes.splice(0)) scope.stop();
    get.mockReset();
});

describe('website replay information', () => {
    it('loads metadata once per replay id and leaves empty rankings intact', async () => {
        get.mockResolvedValue(response(data()));
        const state = setup();
        await vi.waitFor(() => {
            expect(state.info.value).toEqual(data());
        });
        expect(state.loading.value).toBe(false);
        expect(get).toHaveBeenCalledOnce();
        expect(get.mock.calls[0][0]).toBe('/api/common/video/42/analyzer-info');
    });

    it('clears old information and ignores a late response when the replay changes or unmounts', async () => {
        let first: ((value: ReturnType<typeof response>) => void) | undefined;
        let second: ((value: ReturnType<typeof response>) => void) | undefined;
        get.mockImplementationOnce(() => new Promise((resolve) => {
            first = resolve;
        }));
        get.mockImplementationOnce(() => new Promise((resolve) => {
            second = resolve;
        }));
        const state = setup();
        const firstSignal = get.mock.calls[0][1]?.signal;
        state.id.value = '43';
        expect(firstSignal?.aborted).toBe(true);
        expect(state.info.value).toBeNull();
        second?.(response(data(43)));
        await vi.waitFor(() => {
            expect(state.info.value?.video.id).toBe(43);
        });
        first?.(response(data(42)));
        await Promise.resolve();
        expect(state.info.value?.video.id).toBe(43);
        const secondSignal = get.mock.calls[1][1]?.signal;
        state.scope.stop();
        expect(secondSignal?.aborted).toBe(true);
        expect(state.info.value).toBeNull();
    });

    it('reports request failure and recovers on the next replay', async () => {
        get.mockRejectedValueOnce(new AxiosError('Forbidden', 'ERR_BAD_REQUEST', undefined, undefined, { status: 403, statusText: 'Forbidden' } as AxiosResponse));
        const state = setup();
        await vi.waitFor(() => {
            expect(state.errorMessage.value).toBe('403 Forbidden');
        });
        expect(state.info.value).toBeNull();
        expect(state.loading.value).toBe(false);
        get.mockResolvedValueOnce(response(data(43)));
        state.id.value = '43';
        await vi.waitFor(() => {
            expect(state.info.value?.video.id).toBe(43);
        });
        expect(state.errorMessage.value).toBe('');
    });
});
