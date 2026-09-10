import $axios from '@/http';
import { Dict2FormData } from '@/utils/forms';
import type { MS_State } from '@/utils/ms_const';

export interface VideoUploadSuccessResponse {
    type: 'success';
    object: 'videomodel';
    category: 'upload';
    data: {
        id: number;
        state: MS_State;
    };
}

export interface VideoUploadErrorResponse {
    type: 'error';
    object?: string;
    obj?: string;
    category?: string;
}

export type VideoUploadResponse = VideoUploadSuccessResponse | VideoUploadErrorResponse;

export interface VideoUploadSuccessResult {
    type: 'success';
    id: number;
    state: MS_State;
}

export type VideoUploadErrorStatus = 'collision' | 'censorship' | 'upload';

export interface VideoUploadErrorResult {
    type: 'error';
    status: VideoUploadErrorStatus;
}

export type VideoUploadResult = VideoUploadSuccessResult | VideoUploadErrorResult;

export function normalizeVideoUploadResponse(response: VideoUploadResponse): VideoUploadResult {
    if (response.type === 'success') {
        return {
            type: 'success',
            id: response.data.id,
            state: response.data.state,
        };
    }
    if (response.object === 'file') {
        return { type: 'error', status: 'collision' };
    }
    if (response.object === 'identifier') {
        return { type: 'error', status: 'censorship' };
    }
    return { type: 'error', status: 'upload' };
}

export async function uploadVideoFile(file: File): Promise<VideoUploadResult> {
    const { data } = await $axios.post<VideoUploadResponse>('/common/uploadvideo/', Dict2FormData({ file }));
    return normalizeVideoUploadResponse(data);
}
