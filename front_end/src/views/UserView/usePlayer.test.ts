import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { effectScope, nextTick, ref } from 'vue';
import type { EffectScope } from 'vue';

import { usePlayer } from './usePlayer';

import { httpErrorNotification } from '@/components/Notifications';
import { fetchUserInfo } from '@/services/userService';
import { store } from '@/store';
import { UserProfile } from '@/utils/userprofile';

vi.mock('@/services/userService', () => ({ fetchUserInfo: vi.fn() }));
vi.mock('@/components/Notifications', () => ({ httpErrorNotification: vi.fn() }));
vi.mock('@/store', async () => {
    const { reactive } = await import('vue');
    const { UserProfile: Profile } = await import('@/utils/userprofile');
    return { store: reactive({ user: new Profile(), player: new Profile() }) };
});

const scopes: EffectScope[] = [];
function setup(id = 2418) {
    const userId = ref(id);
    const scope = effectScope();
    scopes.push(scope);
    const loading = scope.run(() => usePlayer(() => userId.value));
    if (!loading) throw new Error('Player scope did not start');
    return { userId, scope, loading };
}

describe('personal page player synchronization', () => {
    beforeEach(() => {
        vi.resetAllMocks();
        store.user = new UserProfile();
        store.player = new UserProfile();
    });

    afterEach(() => {
        scopes.splice(0).forEach((scope) => {
            scope.stop();
        });
    });

    it('keeps profile edits visible when a profile request finishes after login restoration', async () => {
        const pending = Promise.withResolvers<UserProfile>();
        vi.mocked(fetchUserInfo).mockReturnValue(pending.promise);
        const { loading } = setup();
        expect(fetchUserInfo).toHaveBeenCalledWith(2418, true);

        store.user = new UserProfile({ id: 2418, username: 'testUser' });
        await nextTick();
        expect(store.player).toBe(store.user);
        expect(loading.value).toBe(false);

        pending.resolve(new UserProfile({ id: 2418, username: 'testUser' }));
        await pending.promise;
        await nextTick();
        store.user.realname = 'testName';
        store.user.signature = 'testSignature';
        expect(store.player.realname).toBe('testName');
        expect(store.player.signature).toBe('testSignature');
        expect(store.player).toBe(store.user);
    });

    it('ignores an old route response without clearing the current loading state', async () => {
        const previous = Promise.withResolvers<UserProfile>();
        const current = Promise.withResolvers<UserProfile>();
        vi.mocked(fetchUserInfo).mockReturnValueOnce(previous.promise).mockReturnValueOnce(current.promise);
        const { userId, loading } = setup(1);
        userId.value = 2;
        await nextTick();

        previous.resolve(new UserProfile({ id: 1 }));
        await previous.promise;
        expect(store.player.id).toBe(0);
        expect(loading.value).toBe(true);

        current.resolve(new UserProfile({ id: 2 }));
        await current.promise;
        expect(store.player.id).toBe(2);
        expect(loading.value).toBe(false);
    });

    it('follows replacement of the logged-in user even when the id stays the same', async () => {
        store.user = new UserProfile({ id: 2418 });
        setup();
        store.user = new UserProfile({ id: 2418, signature: 'new session' });
        await nextTick();
        expect(store.player).toBe(store.user);
        expect(store.player.signature).toBe('new session');
        expect(fetchUserInfo).not.toHaveBeenCalled();
    });

    it('ignores request failures after leaving the page', async () => {
        const pending = Promise.withResolvers<UserProfile>();
        vi.mocked(fetchUserInfo).mockReturnValue(pending.promise);
        const { scope } = setup();
        scope.stop();
        pending.reject(new Error('late failure'));
        await nextTick();
        expect(httpErrorNotification).not.toHaveBeenCalled();
    });

    it('reports current request failures and stops loading', async () => {
        const error = new Error('profile unavailable');
        vi.mocked(fetchUserInfo).mockRejectedValue(error);
        const { loading } = setup();
        await nextTick();
        expect(httpErrorNotification).toHaveBeenCalledWith(error);
        expect(loading.value).toBe(false);
    });
});
