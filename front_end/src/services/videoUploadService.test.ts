import { AxiosError, AxiosHeaders } from 'axios';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { normalizeVideoUploadResponse, uploadVideoFile } from './videoUploadService';

import $axios from '@/http';
import { MS_State } from '@/utils/ms_const';

describe('uploadVideoFile', () => {
    afterEach(() => {
        vi.restoreAllMocks();
    });

    it.each([402, 403, 500])('handles HTTP %i with an empty response body', async (status) => {
        const error = new AxiosError('Upload rejected', AxiosError.ERR_BAD_RESPONSE, undefined, undefined, {
            status,
            statusText: '',
            data: '',
            headers: {},
            config: { headers: new AxiosHeaders() },
        });
        vi.spyOn($axios, 'post').mockRejectedValue(error);

        const result = uploadVideoFile(new File(['video'], 'video.avf'));
        if (status === 402) {
            await expect(result).resolves.toEqual({ type: 'error', status: 'quota' });
        } else {
            await expect(result).rejects.toBe(error);
        }
    });

    it('preserves network errors without a response', async () => {
        const error = new AxiosError('Network Error', AxiosError.ERR_NETWORK);
        vi.spyOn($axios, 'post').mockRejectedValue(error);

        await expect(uploadVideoFile(new File(['video'], 'video.avf'))).rejects.toBe(error);
    });
});

describe('normalizeVideoUploadResponse', () => {
    it('maps successful upload response to uploaded video data', () => {
        expect(normalizeVideoUploadResponse({
            type: 'success',
            object: 'videomodel',
            category: 'upload',
            data: {
                id: 42,
                state: MS_State.Official,
            },
        })).toEqual({
            type: 'success',
            id: 42,
            state: MS_State.Official,
        });
    });

    it('maps file errors to upload collision status', () => {
        expect(normalizeVideoUploadResponse({
            type: 'error',
            object: 'file',
        })).toEqual({
            type: 'error',
            status: 'collision',
        });
    });

    it('maps identifier errors to censorship status', () => {
        expect(normalizeVideoUploadResponse({
            type: 'error',
            object: 'identifier',
        })).toEqual({
            type: 'error',
            status: 'censorship',
        });
    });

    it('falls back to generic upload failure for other error responses', () => {
        expect(normalizeVideoUploadResponse({
            type: 'error',
            obj: 'userprofile',
            category: 'realname_required',
        })).toEqual({
            type: 'error',
            status: 'upload',
        });
    });
});
