import { fetchVideoInfo } from '@/services/videoInfoService';
import { videoplayerstore } from '@/store';
import type { MS_Software } from '@/utils/ms_const';
import { getReplayPreviewUrl } from '@/utils/replayLinks';

export async function preview(id: number | undefined | null, software?: MS_Software): Promise<void> {
    if (id === undefined || id === null || id <= 0) return;
    videoplayerstore.id = id;

    try {
        const resolvedSoftware = software ?? (await fetchVideoInfo(id)).software;
        if (videoplayerstore.id !== id) return;
        videoplayerstore.software = resolvedSoftware;
    } catch (e) {
        videoplayerstore.error = e;
        return;
    }

    videoplayerstore.url = getReplayPreviewUrl(videoplayerstore.id, videoplayerstore.software);
    videoplayerstore.visible = true;
}
