import { beforeEach, describe, expect, it, vi } from 'vitest';

const fetchVideoInfo = vi.hoisted(() => vi.fn());
const videoplayerstore = vi.hoisted(() => ({
    visible: false,
    id: 0,
    software: 'a',
    url: '',
    error: null,
}));

vi.mock('@/services/videoInfoService', () => ({ fetchVideoInfo }));
vi.mock('@/store', () => ({ videoplayerstore }));

describe('preview', () => {
    beforeEach(() => {
        fetchVideoInfo.mockReset();
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
        fetchVideoInfo.mockResolvedValue({ software: 'e' });

        await preview(12);

        expect(fetchVideoInfo).toHaveBeenCalledWith(12);
        expect(videoplayerstore.software).toBe('e');
        expect(videoplayerstore.url).toContain('/api/video/preview?id=12.evf');
        expect(videoplayerstore.visible).toBe(true);
    });

    it('uses the provided software without fetching it again', async () => {
        const { preview } = await import('./PlayerDialog');

        await preview(34, 'r');

        expect(fetchVideoInfo).not.toHaveBeenCalled();
        expect(videoplayerstore.software).toBe('r');
        expect(videoplayerstore.url).toContain('/api/video/preview?id=34.rmv');
        expect(videoplayerstore.visible).toBe(true);
    });
});
