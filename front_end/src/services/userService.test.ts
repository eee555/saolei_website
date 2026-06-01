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
        userGet.mockResolvedValue(createLocalUser(7, fixedNow.getTime() - 1000));
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

    it('ignores local database read errors and continues through the mocked request path', async () => {
        const freshUser = createUserInfo(12);
        userGet.mockRejectedValue(new Error('database unavailable'));
        axiosGet.mockResolvedValue({ data: freshUser });

        const fetchUserInfo = await importFetchUserInfo();
        const result = await fetchUserInfo(12);

        expect(result).toEqual(freshUser);
        expect(axiosGet).toHaveBeenCalledWith('/api/userprofile/info/12');
        expect(userPut).toHaveBeenCalledWith({
            ...freshUser,
            updatedAt: fixedNow.getTime(),
        });
    });
});
