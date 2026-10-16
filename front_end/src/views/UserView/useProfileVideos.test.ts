import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { effectScope, nextTick, reactive, ref } from 'vue';
import type { EffectScope } from 'vue';

import { useProfileVideos } from './useProfileVideos';

import { invalidateProfileData } from '@/services/profileDataService';
import { fetchUserVideos } from '@/services/userService';
import { store } from '@/store';
import { LoginStatus } from '@/utils/common/structInterface';
import { UserProfile } from '@/utils/userprofile';
import { VideoAbstract } from '@/utils/videoabstract';

vi.mock('@/services/userService', () => ({ fetchUserVideos: vi.fn() }));
vi.mock('vue-router', () => ({ useRoute: () => route }));
vi.mock('vue', async (original) => ({ ...await original<Record<string, unknown>>(), onActivated: vi.fn(), onDeactivated: vi.fn() }));
vi.mock('@/store', async () => {
    const { reactive: makeReactive } = await import('vue');
    return { store: makeReactive({ user: { id: 42 }, login_status: 'i', sessionRevision: 0 }) };
});

const route = reactive({ name: 'user-videos', params: { id: '42' } });
const scopes: EffectScope[] = [];
function setup() {
    const user = ref(new UserProfile({ id: 42 }));
    const scope = effectScope();
    scopes.push(scope);
    const state = scope.run(() => useProfileVideos(user));
    if (!state) throw new Error('Video scope did not start');
    return { user, ...state };
}
const makeVideos = (id: number) => [new VideoAbstract({ id, level: 'e', bv: 100, timems: 40000, state: 'c', software: 'e', mode: '00' })];

describe('profile videos request lifecycle', () => {
    beforeEach(() => {
        vi.resetAllMocks();
        route.name = 'user-videos';
        route.params.id = '42';
        store.user.id = 42;
        store.login_status = LoginStatus.IsLogin;
        store.sessionRevision = 0;
    });
    afterEach(() => {
        scopes.splice(0).forEach((scope) => {
            scope.stop();
        });
    });

    it('does not download for an inactive page and reuses completed data on reactivation', async () => {
        route.name = 'user-summary';
        vi.mocked(fetchUserVideos).mockResolvedValue(makeVideos(1));
        const { videos, valid } = setup();
        expect(fetchUserVideos).not.toHaveBeenCalled();
        route.name = 'user-videos';
        await nextTick();
        await nextTick();
        expect(videos.value[0].id).toBe(1);
        expect(valid.value).toBe(true);
        route.name = 'user-settings';
        await nextTick();
        expect(videos.value).toEqual([]);
        route.name = 'user-videos';
        await nextTick();
        expect(fetchUserVideos).toHaveBeenCalledTimes(1);
        expect(videos.value[0].id).toBe(1);
    });

    it('handles out-of-order responses without replacing the current player or ending its loading', async () => {
        const previous = Promise.withResolvers<VideoAbstract[]>();
        const current = Promise.withResolvers<VideoAbstract[]>();
        vi.mocked(fetchUserVideos).mockReturnValueOnce(previous.promise).mockReturnValueOnce(current.promise);
        const { user, videos, loading } = setup();
        route.params.id = '43';
        user.value = new UserProfile({ id: 43 });
        await nextTick();
        previous.resolve(makeVideos(1));
        await previous.promise;
        expect(loading.value).toBe(true);
        expect(videos.value).toEqual([]);
        current.resolve(makeVideos(2));
        await current.promise;
        expect(videos.value[0].id).toBe(2);
        expect(loading.value).toBe(false);
    });

    it('discards owner data and late owner responses after logout, then loads public data', async () => {
        const owner = Promise.withResolvers<VideoAbstract[]>();
        const publicData = Promise.withResolvers<VideoAbstract[]>();
        vi.mocked(fetchUserVideos).mockReturnValueOnce(owner.promise).mockReturnValueOnce(publicData.promise);
        const { user, videos, loading } = setup();
        store.user.id = 0;
        store.login_status = LoginStatus.NotLogin;
        store.sessionRevision++;
        await nextTick();
        owner.resolve(makeVideos(99));
        await owner.promise;
        expect(user.value.videos).toBeUndefined();
        expect(videos.value).toEqual([]);
        expect(loading.value).toBe(true);
        publicData.resolve(makeVideos(1));
        await publicData.promise;
        expect(videos.value[0].id).toBe(1);
    });

    it('invalidates in the background without fetching and retries failures explicitly', async () => {
        vi.mocked(fetchUserVideos).mockResolvedValue(makeVideos(1));
        const { failed, loading, refresh, videos } = setup();
        await nextTick();
        route.name = 'user-settings';
        await nextTick();
        invalidateProfileData(42);
        await nextTick();
        expect(fetchUserVideos).toHaveBeenCalledTimes(1);
        vi.mocked(fetchUserVideos).mockRejectedValueOnce(new Error('network'));
        route.name = 'user-videos';
        await nextTick();
        await nextTick();
        expect(failed.value).toBe(true);
        expect(loading.value).toBe(false);
        expect(videos.value).toEqual([]);
        await refresh();
        expect(failed.value).toBe(false);
        expect(videos.value[0].id).toBe(1);
    });
});
