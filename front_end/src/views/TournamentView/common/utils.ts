import type { VideoAbstract } from '@/utils/videoabstract';

export interface AutoUploadVideo {
    filename: string;
    stat: VideoAbstract;
    identifier: string;
    tokens: string[];
}
