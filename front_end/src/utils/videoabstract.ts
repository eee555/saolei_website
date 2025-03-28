import { toISODateString } from './datetime';
import { MS_Level, MS_Software, STNB_const } from './ms_const';

export interface VideoAbstractInfo {
    id: number,
    upload_time: string | Date,
    level: MS_Level,
    mode: string,
    timems: number,
    bv: number,
    state: string,
    software: string,
    cl: number | null,
    ce: number | null,
}

interface VideoRedisInfo {
    state: string,
    software: string,
    time: string,
    player: string,
    player_id: number,
    level: MS_Level,
    mode: string,
    timems: number,
    bv: number,
    identifier: string,
    cl?: number,
    ce?: number,
}

export type getStat_stat = 'time' | 'bvs' | 'timems' | 'bv' | 'qg' | 'rqp' | 'stnb' | 'cl' | 'ioe' | 'thrp' | 'corr';

export class VideoAbstract {
    public id?: number;
    public upload_time: Date;
    public level: MS_Level;
    public mode: string;
    public timems: number;
    public bv: number;
    public state: string;
    public software: MS_Software;
    public cl?: number;
    public ce?: number;
    public player_id?: number;
    public player_name?: string;

    constructor(info: any) {
        if (info.id) this.id = info.id;
        else throw new Error('录像信息未包含id');

        if (info.upload_time) this.upload_time = new Date(info.upload_time);
        else if (info.time) this.upload_time = new Date(info.time); // newest_queue等返回的
        else throw new Error('录像信息未包含上传时间');

        this.level = info.level;
        this.mode = info.mode;
        this.timems = info.timems;
        this.bv = info.bv;
        this.state = info.state;
        this.software = info.software;

        if (info.cl) this.cl = info.cl;
        if (info.ce) this.ce = info.ce;
        if (info.player_id) this.player_id = info.player_id;
        if (info.player_name) this.player_name = info.player_name;
    }

    static fromVideoAbstractInfo(info: VideoAbstractInfo): VideoAbstract {
        return new VideoAbstract(info);
    }

    static fromVideoRedisInfo(key: number, info: VideoRedisInfo): VideoAbstract {
        return new VideoAbstract({
            id: key,
            upload_time: new Date(info.time),
            level: info.level,
            mode: info.mode,
            timems: info.timems,
            bv: info.bv,
            state: info.state,
            software: info.software,
            player_id: info.player_id,
            player_name: info.player,
            cl: info.cl,
            ce: info.ce,
        })
    }

    public time() {
        return this.timems / 1000;
    }

    public bvs() {
        return this.bv / this.time();
    }

    public qg() {
        return Math.pow(this.time(), 1.7) / this.bv;
    }

    public rqp() {
        return this.time() * (this.time() - 1) / this.bv;
    }

    public stnb() {
        return STNB_const.value[this.level] / this.qg();
    }

    public ioe() {
        if (this.cl === undefined) return undefined;
        return this.bv / this.cl;
    }

    public thrp() {
        if (this.ce === undefined) return undefined;
        return this.bv / this.ce;
    }

    public corr() {
        if (this.cl === undefined || this.ce === undefined) return undefined;
        return this.ce / this.cl;
    }

    public getStat(stat: getStat_stat) {
        switch (stat) {
            case 'time': return this.time();
            case 'bvs': return this.bvs();
            case 'timems': return this.timems;
            case 'bv': return this.bv;
            case 'qg': return this.qg();
            case 'rqp': return this.rqp();
            case 'stnb': return this.stnb();
            case 'cl': return this.cl;
            case 'ioe': return this.ioe();
            case 'thrp': return this.thrp();
            case 'corr': return this.corr();
        }
    }

    public displayStat(stat: getStat_stat) {
        switch (stat) {
            case 'time': return this.time().toFixed(3);
            case 'bvs': return this.bvs().toFixed(3);
            case 'bv': return this.bv.toString();
            case 'qg': return this.qg().toFixed(3);
            case 'rqp': return this.rqp().toFixed(3);
            case 'stnb': return this.stnb().toFixed(1);
            case 'cl': {
                const cl = this.cl;
                return cl === undefined ? "-" : cl.toString();
            }
            case 'ioe': {
                const ioe = this.ioe();
                return ioe === undefined ? "-" : ioe.toFixed(3);
            }
            case 'thrp': {
                const thrp = this.thrp();
                return thrp === undefined ? "-" : thrp.toFixed(3);
            }
            case 'corr': {
                const corr = this.corr();
                return corr === undefined ? "-" : corr.toFixed(3);
            }
        }
    }

    public tooltipFormatter(t: any) {
        // t is the localization API from i18n
        return `${t('common.prop.upload_time')}: ${this.upload_time} <br>
        ${t('common.level.' + this.level)} ${this.bv}Bv = ${this.time().toFixed(3)} * ${this.bvs().toFixed(3)}`
    }
}

export function groupVideosByUploadDate(videos: VideoAbstract[]): Map<string, VideoAbstract[]> {
    const result = new Map<string, VideoAbstract[]>();

    videos.forEach(video => {
        const dateKey = toISODateString(video.upload_time); // Extract date part as string (YYYY-MM-DD)
        if (!result.has(dateKey)) {
            result.set(dateKey, []);
        }
        result.get(dateKey)?.push(video);
    });

    return result;
}

export function groupVideosByBBBv(videos: VideoAbstract[], level: MS_Level): Map<number, VideoAbstract[]> {
    const result = new Map<number, VideoAbstract[]>();

    videos.forEach(video => {
        if (video.level !== level) {
            return;
        }
        const bbbv = video.bv;
        if (!result.has(bbbv)) {
            result.set(bbbv, []);
        }
        result.get(bbbv)?.push(video);
    });

    return result;
}