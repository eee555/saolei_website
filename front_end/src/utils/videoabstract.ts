import { toISODateString } from './datetime';
import { MS_Level, MS_Software, MS_State, STNB_const } from './ms_const';

function undefinedOrToString(value: any): string | undefined {
    return value === undefined ? undefined : value.toString();
}

function undefinedOrToFixed(value: any, digits: number): string | undefined {
    return value === undefined ? undefined : value.toFixed(digits);
}

function undefinedDivideNumber(a: number | undefined, b: number): number | undefined {
    if (a === undefined) return undefined;
    return a / b;
}
function numberDivideUndefined(a: number, b: number | undefined): number | undefined {
    if (b === undefined) return undefined;
    return a / b;
}
function undefinedDivideUndefined(a: number | undefined, b: number | undefined): number | undefined {
    if (a === undefined || b === undefined) return undefined;
    return a / b;
}

export interface VideoAbstractInfo {
    id: number;
    upload_time: string | Date;
    end_time: Date | null;
    level: MS_Level;
    mode: string;
    timems: number;
    bv: number;
    state: string;
    software: string;
    cl: number | null;
    ce: number | null;
    file_size: number;
}

interface VideoRedisInfo {
    state: string;
    software: string;
    time: string;
    player: string;
    player_id: number;
    level: MS_Level;
    mode: string;
    timems: number;
    bv: number;
    identifier: string;
    cl?: number;
    ce?: number;
}

export type getStat_stat = 'time' | 'bvs' | 'timems' | 'bv' | 'qg' | 'rqp' | 'stnb' | 'ce' | 'ces' | 'cl' | 'cls' | 'ioe' | 'thrp' | 'corr' | 'path' | 'mov' | 'iome';

export class VideoAbstract {
    public id: number;
    public upload_time: Date;
    public end_time?: Date;
    public level: MS_Level;
    public mode: string;
    public timems: number;
    public bv: number;
    public state: MS_State;
    public software: MS_Software;
    public cl?: number;
    public ce?: number;
    public path?: number;
    public player_id?: number;
    public player_name?: string;
    public file_size: number;
    public ongoing_tournament?: boolean;

    constructor(info: any) {
        if (info.id) this.id = info.id;
        else this.id = 0;

        if (info.upload_time) this.upload_time = new Date(info.upload_time);
        else if (info.time) this.upload_time = new Date(info.time); // newest_queue等返回的
        else this.upload_time = new Date();

        if (info.end_time) this.end_time = new Date(info.end_time);

        this.level = info.level;
        this.mode = info.mode;
        this.timems = info.timems;
        this.bv = info.bv;
        this.state = info.state;
        this.software = info.software;

        if (info.cl) this.cl = info.cl;
        if (info.ce) this.ce = info.ce;
        if (info.path) this.path = info.path;
        if (info.player_id) this.player_id = info.player_id;
        if (info.player_name) this.player_name = info.player_name;

        if (info.file_size) this.file_size = info.file_size;
        else this.file_size = 0;

        if (info.ongoing_tournament) this.ongoing_tournament = info.ongoing_tournament;
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
        });
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
        return numberDivideUndefined(this.bv, this.cl);
    }

    public thrp() {
        return numberDivideUndefined(this.bv, this.ce);
    }

    public corr() {
        return undefinedDivideUndefined(this.ce, this.cl);
    }

    public cls() {
        return undefinedDivideNumber(this.cl, this.time());
    }

    public ces() {
        return undefinedDivideNumber(this.ce, this.time());
    }

    public mov() {
        return undefinedDivideNumber(this.path, this.time());
    }

    public iome() {
        return numberDivideUndefined(this.bv, this.path);
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
            case 'ce': return this.ce;
            case 'ces': return this.ces();
            case 'cl': return this.cl;
            case 'cls': return this.cls();
            case 'ioe': return this.ioe();
            case 'thrp': return this.thrp();
            case 'corr': return this.corr();
            case 'path': return this.path;
            case 'mov': return this.mov();
            case 'iome': return this.iome();
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
            case 'ce': return undefinedOrToString(this.ce);
            case 'ces': return undefinedOrToFixed(this.ces(), 3);
            case 'cl': return undefinedOrToString(this.cl);
            case 'cls': return undefinedOrToFixed(this.cls(), 3);
            case 'ioe': return undefinedOrToFixed(this.ioe(), 3);
            case 'thrp': return undefinedOrToFixed(this.thrp(), 3);
            case 'corr': return undefinedOrToFixed(this.corr(), 3);
            case 'path': return undefinedOrToFixed(this.path, 0);
            case 'mov': return undefinedOrToFixed(this.mov(), 3);
            case 'iome': return undefinedOrToFixed(this.iome(), 3);
        }
    }

    public tooltipFormatter(t: any) {
        // t is the localization API from i18n
        return `${t('common.prop.upload_time')}: ${this.upload_time} <br>
        ${t('common.level.' + this.level)} ${this.bv}Bv = ${this.time().toFixed(3)} * ${this.bvs().toFixed(3)}`;
    }
}

export function groupVideosByDate(videos: VideoAbstract[], attr: 'upload_time' | 'end_time' = 'upload_time'): Map<string, VideoAbstract[]> {
    const result = new Map<string, VideoAbstract[]>();

    videos.forEach((video) => {
        let date = video[attr];
        if (!date) date = video.upload_time; // fallback to upload_time if end_time is not available
        const dateKey = toISODateString(date); // Extract date part as string (YYYY-MM-DD)
        if (!result.has(dateKey)) {
            result.set(dateKey, []);
        }
        result.get(dateKey)?.push(video);
    });

    return result;
}

export function groupVideosByBBBv(videos: VideoAbstract[], level: MS_Level): Map<number, VideoAbstract[]> {
    const result = new Map<number, VideoAbstract[]>();

    videos.forEach((video) => {
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
