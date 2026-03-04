import { MS_Level } from '@/utils/ms_const';

export enum SaoleiVideoImportState {
    NOTPLANNED = 'n',
    IMPORTING = 'i',
    IMPORTED = 'd',
    FAILED = 'f',
}

export interface SaoleiVideo {
    id: number;
    level: MS_Level;
    timems: number;
    bv: number;
    nf: boolean;
    upload_time: Date;
    import_state: SaoleiVideoImportState;
    import_video?: number;
}

export function saoleiVideoFromResponse(data: any): SaoleiVideo {
    return {
        id: data.id,
        level: data.level,
        timems: data.timems,
        bv: data.bv,
        nf: data.nf,
        upload_time: new Date(data.upload_time),
        import_state: data.import_state,
        import_video: data.import_video,
    };
}

export interface VideoImportEvent {
    time: Date;
    type: 'start' | 'success' | 'error' | 'getList' | 'pageEnd' | 'pageError' | 'noVideo' | 'newVideo' | 'consoleError';
    count?: number;
    video?: SaoleiVideo;
    error?: any;
}

export interface PageImportEvent {
    time: Date;
    type: 'start' | 'normal' | 'end';
    pageNumber: number;
    videoEvents: VideoImportEvent[];
}
