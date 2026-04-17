import { UploadVideoForm } from '@/utils/fileIO';
import { VideoAbstract } from '@/utils/videoabstract';

export const UploadStatus = ['parse', 'pass', 'filename', 'fileext', 'custom', 'invalid', 'identifier', 'needApprove', 'censorship', 'collision', 'upload', 'process', 'success'] as const;
export type UploadStatus = typeof UploadStatus[number];

export interface UploadEntry {
    hash: string;
    filename: string;
    status: UploadStatus;
    form: UploadVideoForm | null; // for upload
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

export function simpleHash(file: File) {
    return `${file.name}_${file.size}_${file.lastModified}`;
}
