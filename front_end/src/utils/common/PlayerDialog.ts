import $axios from '@/http';
import { videoplayerstore } from '@/store';
import { MS_Software } from '@/utils/ms_const';
import { getSoftwareExtension } from '@/utils/strings';

async function fetchSoftware(id: number) {
    const response = await $axios.get('/video/get_software/', { params: { id } });
    return response.data.msg as MS_Software;
}

function generateURL(id: number, software: MS_Software) {
    return import.meta.env.VITE_BASE_API + '/video/preview/?id=' + id + getSoftwareExtension(software);
}

export async function preview(id: number | undefined | null) {
    if (!id) return;
    videoplayerstore.id = id;

    try {
        videoplayerstore.software = await fetchSoftware(videoplayerstore.id);
    } catch (e) {
        videoplayerstore.error = e;
    }

    videoplayerstore.url = generateURL(videoplayerstore.id, videoplayerstore.software);
    videoplayerstore.visible = true;
}
