import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import type { LocalUser } from '@/services/localDatabase';
import type { GetUserInfoResponse } from '@/utils/common/structInterface';

const createUserInfo = (id: number): GetUserInfoResponse => ({
    id,
    username: `user-${id}`,
    firstname: '',
    lastname: '',
    realname: '',
    is_banned: false,
    is_staff: false,
    country: '',
    signature: '',
    last_change_avatar: '',
    last_change_signature: '',
    left_avatar_n: 0,
    left_signature_n: 0,
});

const createLocalUser = (id: number, updatedAt: number): LocalUser => ({
    ...createUserInfo(id),
    updatedAt,
});

describe('userService local user database behavior', () => {
    const fixedNow = new Date('2026-06-01T12:00:00Z');
    let userGet: ReturnType<typeof vi.fn>;
    let userPut: ReturnType<typeof vi.fn>;
    let userDelete: ReturnType<typeof vi.fn>;
    let axiosGet: ReturnType<typeof vi.fn>;

    async function importFetchUserInfo() {
        vi.doMock('@/http', () => ({
            default: {
                get: axiosGet,
            },
        }));

        vi.doMock('@/services/localDatabase', () => ({
            localDatabase: {
                users: {
                    get: userGet,
                    put: userPut,
                    delete: userDelete,
                },
            },
        }));

        const module = await import('./userService');
        return module.fetchUserInfo;
    }

    beforeEach(() => {
        vi.resetModules();
        vi.useFakeTimers();
        vi.setSystemTime(fixedNow);

        userGet = vi.fn();
        userPut = vi.fn();
        userDelete = vi.fn();
        axiosGet = vi.fn();
    });

    afterEach(() => {
        vi.doUnmock('@/http');
        vi.doUnmock('@/services/localDatabase');
        vi.useRealTimers();
    });

    it('returns a fresh local user without requesting the network', async () => {
        userGet.mockResolvedValue(createLocalUser(7, fixedNow.getTime()));

        const fetchUserInfo = await importFetchUserInfo();
        const result = await fetchUserInfo(7);

        expect(result).toEqual(createUserInfo(7));
        expect(userGet).toHaveBeenCalledWith(7);
        expect(axiosGet).not.toHaveBeenCalled();
        expect(userPut).not.toHaveBeenCalled();
        expect(userDelete).not.toHaveBeenCalled();
    });

    it('deletes expired local user data before falling back to the mocked request path', async () => {
        const freshUser = createUserInfo(7);
        freshUser.username = 'fresh-user';
        userGet.mockResolvedValue(createLocalUser(7, fixedNow.getTime() - 24 * 60 * 60 * 1000));
        axiosGet.mockResolvedValue({ data: freshUser });

        const fetchUserInfo = await importFetchUserInfo();
        const result = await fetchUserInfo(7);

        expect(result).toEqual(freshUser);
        expect(userDelete).toHaveBeenCalledWith(7);
        expect(axiosGet).toHaveBeenCalledWith('/api/userprofile/info/7');
        expect(userPut).toHaveBeenCalledWith({
            ...freshUser,
            updatedAt: fixedNow.getTime(),
        });
    });

    it('throws local database read errors without requesting the network', async () => {
        const databaseError = new Error('database unavailable');
        userGet.mockRejectedValue(databaseError);

        const fetchUserInfo = await importFetchUserInfo();

        await expect(fetchUserInfo(12)).rejects.toThrow(databaseError);
        expect(axiosGet).not.toHaveBeenCalled();
        expect(userPut).not.toHaveBeenCalled();
    });

    it('throws local database write errors after fetching user info', async () => {
        const freshUser = createUserInfo(12);
        const databaseError = new Error('database unavailable');
        userGet.mockResolvedValue(null);
        axiosGet.mockResolvedValue({ data: freshUser });
        userPut.mockRejectedValue(databaseError);

        const fetchUserInfo = await importFetchUserInfo();

        await expect(fetchUserInfo(12)).rejects.toThrow(databaseError);
        expect(axiosGet).toHaveBeenCalledWith('/api/userprofile/info/12');
        expect(userPut).toHaveBeenCalledWith({
            ...freshUser,
            updatedAt: fixedNow.getTime(),
        });
    });

    it('limits user info requests to 10 per second', async () => {
        userGet.mockResolvedValue(null);
        axiosGet.mockImplementation((url: string) => {
            const userId = Number(url.split('/').at(-1));
            return Promise.resolve({ data: createUserInfo(userId) });
        });

        const fetchUserInfo = await importFetchUserInfo();
        const firstRequest = fetchUserInfo(1);
        const secondRequest = fetchUserInfo(2);

        await vi.advanceTimersByTimeAsync(0);
        expect(axiosGet).toHaveBeenCalledTimes(1);

        await vi.advanceTimersByTimeAsync(99);
        expect(axiosGet).toHaveBeenCalledTimes(1);

        await vi.advanceTimersByTimeAsync(1);
        expect(axiosGet).toHaveBeenCalledTimes(2);

        await expect(Promise.all([firstRequest, secondRequest])).resolves.toEqual([
            createUserInfo(1),
            createUserInfo(2),
        ]);
    });

    it('pauses the whole queue for one minute and retries when the backend returns 429', async () => {
        userGet.mockResolvedValue(null);
        const firstUser = createUserInfo(1);
        const secondUser = createUserInfo(2);

        axiosGet.mockImplementation((url: string) => {
            if (url.endsWith('/1') && axiosGet.mock.calls.filter(([calledUrl]) => calledUrl === url).length === 1) {
                return Promise.reject({ response: { status: 429 } });
            }

            return Promise.resolve({
                data: url.endsWith('/1') ? firstUser : secondUser,
            });
        });

        const fetchUserInfo = await importFetchUserInfo();
        const firstRequest = fetchUserInfo(1);
        const secondRequest = fetchUserInfo(2);

        await vi.advanceTimersByTimeAsync(0);
        expect(axiosGet).toHaveBeenCalledTimes(1);

        await vi.advanceTimersByTimeAsync(59_999);
        expect(axiosGet).toHaveBeenCalledTimes(1);

        await vi.advanceTimersByTimeAsync(1);
        expect(axiosGet).toHaveBeenCalledTimes(2);
        expect(axiosGet).toHaveBeenNthCalledWith(2, '/api/userprofile/info/1');

        await vi.advanceTimersByTimeAsync(99);
        expect(axiosGet).toHaveBeenCalledTimes(2);

        await vi.advanceTimersByTimeAsync(1);
        expect(axiosGet).toHaveBeenCalledTimes(3);
        expect(axiosGet).toHaveBeenNthCalledWith(3, '/api/userprofile/info/2');

        await expect(Promise.all([firstRequest, secondRequest])).resolves.toEqual([firstUser, secondUser]);
    });
});
