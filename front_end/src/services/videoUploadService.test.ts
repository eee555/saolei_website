import { describe, expect, it } from 'vitest';

import { normalizeVideoUploadResponse } from './videoUploadService';

import { MS_State } from '@/utils/ms_const';

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
