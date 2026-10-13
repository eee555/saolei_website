import $axios from '@/http';
import { videoplayerstore } from '@/store';
import type { MS_Software } from '@/utils/ms_const';
import { getReplayPreviewUrl } from '@/utils/replayLinks';

interface SoftwareResponse {
    msg: MS_Software;
}

async function fetchSoftware(id: number) {
    const response = await $axios.get<SoftwareResponse>('/video/get_software/', { params: { id } });
    return response.data.msg;
}

export async function preview(id: number | undefined | null, software?: MS_Software): Promise<void> {
    if (id === undefined || id === null || id <= 0) return;
    videoplayerstore.id = id;

    try {
        videoplayerstore.software = software ?? await fetchSoftware(videoplayerstore.id);
    } catch (e) {
        videoplayerstore.error = e;
    }

    videoplayerstore.url = getReplayPreviewUrl(videoplayerstore.id, videoplayerstore.software);
    videoplayerstore.visible = true;
}
