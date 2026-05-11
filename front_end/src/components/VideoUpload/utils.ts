import { getFileExtension } from '@/utils/strings';
import { VideoAbstract } from '@/utils/videoabstract';

export const UploadStatus = ['parse', 'pass', 'filename', 'filesize', 'fileext', 'custom', 'invalid', 'identifier', 'needApprove', 'censorship', 'collision', 'upload', 'process', 'success'] as const;
export type UploadStatus = typeof UploadStatus[number];

export interface UploadEntry {
    hash: string;
    file: File;
    status: UploadStatus;
    stat: VideoAbstract | null; // for display
}

export interface ParserProgress {
    total: number;
    parsed: number;
}

export interface UploadProgress {
    total: number;
    uploaded: number;
    failed: number;
}

export function fileCollide(e1: UploadEntry, e2: UploadEntry) {
    return e1.hash === e2.hash && getFileExtension(e1.file.name) === getFileExtension(e2.file.name);
}
