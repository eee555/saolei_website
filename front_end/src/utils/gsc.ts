import { GSCDefaults, isStandardLevel, MS_Mode } from './ms_const';
import { TournamentParticipant } from './tournaments';
import type { VideoAbstract } from './videoabstract';

export const GSCBVMin = { b: 10, i: 30, e: 100 } as const;

export function isGSCSupportedVideo(video: VideoAbstract): boolean {
    return isStandardLevel(video.level) && (video.mode === MS_Mode.Standard || video.mode === MS_Mode.NoFlag);
}

export function meetsGSCBV(video: VideoAbstract): boolean {
    return isStandardLevel(video.level) && video.bv >= GSCBVMin[video.level];
}

export interface GSCInfo {
    id: number;
    start_time?: Date;
    end_time?: Date;
    token?: string;
}

export class GSCParticipant extends TournamentParticipant {
    public bt1st: number = GSCDefaults.bt;
    public bt20th: number = GSCDefaults.bt;
    public bt20sum: number = GSCDefaults.bt * 20;
    public it1st: number = GSCDefaults.it;
    public it12th: number = GSCDefaults.it;
    public it12sum: number = GSCDefaults.it * 12;
    public et1st: number = GSCDefaults.et;
    public et5th: number = GSCDefaults.et;
    public et5sum: number = GSCDefaults.et * 5;

    public constructor(init: Partial<GSCParticipant> = {}) {
        super(init);
        Object.assign(this, init);
    }

    public get sum_tbest(): number {
        return this.bt1st + this.it1st + this.et1st;
    }

    public get sum_tedge(): number {
        return this.bt20th + this.it12th + this.et5th;
    }

    public get sum_tsum(): number {
        return this.bt20sum + this.it12sum + this.et5sum;
    }
}
