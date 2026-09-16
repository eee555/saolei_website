import { beforeEach, describe, expect, it, vi } from 'vitest';

const axiosGet = vi.hoisted(() => vi.fn());
const videoplayerstore = vi.hoisted(() => ({
    visible: false,
    id: 0,
    software: 'a',
    url: '',
    error: null,
}));

vi.mock('@/http', () => ({ default: { get: axiosGet } }));
vi.mock('@/store', () => ({ videoplayerstore }));

describe('preview', () => {
    beforeEach(() => {
        axiosGet.mockReset();
        Object.assign(videoplayerstore, {
            visible: false,
            id: 0,
            software: 'a',
            url: '',
            error: null,
        });
    });

    it('fetches the software when the caller does not provide it', async () => {
        const { preview } = await import('./PlayerDialog');
        axiosGet.mockResolvedValue({ data: { msg: 'e' } });

        await preview(12);

        expect(axiosGet).toHaveBeenCalledWith('/video/get_software/', { params: { id: 12 } });
        expect(videoplayerstore.software).toBe('e');
        expect(videoplayerstore.url).toContain('/video/preview/?id=12.evf');
        expect(videoplayerstore.visible).toBe(true);
    });

    it('uses the provided software without fetching it again', async () => {
        const { preview } = await import('./PlayerDialog');

        await preview(34, 'r');

        expect(axiosGet).not.toHaveBeenCalled();
        expect(videoplayerstore.software).toBe('r');
        expect(videoplayerstore.url).toContain('/video/preview/?id=34.rmv');
        expect(videoplayerstore.visible).toBe(true);
    });
});
