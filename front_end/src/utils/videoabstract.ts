/* eslint-disable @typescript-eslint/member-ordering */
import { CustomLevel } from './customlevel';
import { toDate, toISODateString } from './datetime';
import type { MS_Level, MS_Software } from './ms_const';
import { isStandardLevel, MS_State, STNB_const } from './ms_const';
import { formatBytes } from './strings';

type VideoLevel = MS_Level | CustomLevel;
export type StandardVideoAbstract = VideoAbstract & { level: MS_Level };

function undefinedOrToString(value: { toString: () => string } | undefined): string | undefined {
    return value === undefined ? undefined : value.toString();
}

function undefinedOrToFixed(value: number | undefined, digits: number): string | undefined {
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
    level: VideoLevel;
    mode: string;
    timems: number;
    bv: number;
    state: string;
    software: string;
    cl: number | null;
    ce: number | null;
    file_size: number;
    pluck: number | null;
}

interface VideoRedisInfo {
    state: string;
    software: string;
    time: string;
    player_id: number;
    level: VideoLevel;
    mode: string;
    timems: number;
    bv: number;
    identifier: string;
    cl?: number;
    ce?: number;
}

interface VideoAbstractData {
    id?: number;
    upload_time?: string | Date;
    time?: string | Date;
    end_time?: string | Date | null;
    level: string | CustomLevel;
    mode: string;
    timems: number;
    bv: number;
    state?: string;
    software: string;
    cl?: number | null;
    ce?: number | null;
    path?: number | null;
    pluck?: number | null;
    player_id?: number;
    player?: number;
    file_size?: number;
    ongoing_tournament?: boolean;
}

export const getStat_keys = ['time', 'bvs', 'timems', 'bv', 'qg', 'rqp', 'stnb', 'ce', 'ces', 'cl', 'cls', 'ioe', 'thrp', 'corr', 'path', 'pluck', 'npath', 'mov', 'iome', 'file_size'] as const;
export type getStat_stat = typeof getStat_keys[number];

export class VideoAbstract {
    public id = 0;
    public upload_time = new Date();
    public end_time?: Date;
    public level: VideoLevel;
    public mode: string;
    public timems: number;
    public bv: number;
    public state: MS_State = MS_State.Plain;
    public software: MS_Software;
    public cl?: number;
    public ce?: number;
    public path?: number;
    public pluck?: number;
    public player_id?: number;
    public file_size = 0;
    public ongoing_tournament?: boolean;

    public constructor(info: VideoAbstractData) {
        this.id = info.id ?? this.id;

        const uploadTime = info.upload_time ?? info.time;
        if (uploadTime !== undefined) this.upload_time = new Date(uploadTime);

        this.end_time = toDate(info.end_time);

        this.level = parseLevel(info.level);
        this.mode = info.mode;
        this.timems = info.timems;
        this.bv = info.bv;
        if (info.state !== undefined) this.state = info.state as MS_State;
        this.software = info.software as MS_Software;

        this.cl = info.cl ?? undefined;
        this.ce = info.ce ?? undefined;
        this.path = info.path ?? undefined;
        this.pluck = info.pluck ?? undefined;
        this.player_id = info.player_id ?? info.player;

        this.file_size = info.file_size ?? this.file_size;

        this.ongoing_tournament = info.ongoing_tournament ?? undefined;
    }

    public static fromVideoRedisInfo(key: number, info: VideoRedisInfo): VideoAbstract {
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
            cl: info.cl,
            ce: info.ce,
        });
    }

    public get time(): number {
        return this.timems / 1000;
    }

    public get bvs(): number {
        return this.bv / this.time;
    }

    public get qg(): number {
        return Math.pow(this.time, 1.7) / this.bv;
    }

    public get rqp(): number {
        return this.time * (this.time - 1) / this.bv;
    }

    public get stnb(): number {
        if (!isStandardLevel(this.level)) return NaN;
        return STNB_const.value[this.level] / this.qg;
    }

    public get ioe(): number | undefined {
        return numberDivideUndefined(this.bv, this.cl);
    }

    public get thrp(): number | undefined {
        return numberDivideUndefined(this.bv, this.ce);
    }

    public get corr(): number | undefined {
        return undefinedDivideUndefined(this.ce, this.cl);
    }

    public get cls(): number | undefined {
        return undefinedDivideNumber(this.cl, this.time);
    }

    public get ces(): number | undefined {
        return undefinedDivideNumber(this.ce, this.time);
    }

    public get npath(): number | undefined {
        return undefinedDivideNumber(this.path, 16);
    }

    public get mov(): number | undefined {
        return undefinedDivideNumber(this.npath, this.time);
    }

    public get iome(): number | undefined {
        return numberDivideUndefined(this.bv, this.npath);
    }

    public getStat(stat: getStat_stat): number | undefined {
        return this[stat];
    }

    public displayStat(stat: getStat_stat): string | undefined {
        switch (stat) {
            case 'timems':
            case 'time': return this.time.toFixed(3);
            case 'bvs': return this.bvs.toFixed(3);
            case 'bv': return this.bv.toString();
            case 'qg': return this.qg.toFixed(3);
            case 'rqp': return this.rqp.toFixed(3);
            case 'stnb': return this.stnb.toFixed(1);
            case 'ce': return undefinedOrToString(this.ce);
            case 'ces': return undefinedOrToFixed(this.ces, 3);
            case 'cl': return undefinedOrToString(this.cl);
            case 'cls': return undefinedOrToFixed(this.cls, 3);
            case 'ioe': return undefinedOrToFixed(this.ioe, 3);
            case 'thrp': return undefinedOrToFixed(this.thrp, 3);
            case 'corr': return undefinedOrToFixed(this.corr, 3);
            case 'path': return undefinedOrToFixed(this.path, 0);
            case 'pluck': return undefinedOrToFixed(this.pluck, 3);
            case 'npath': return undefinedOrToFixed(this.npath, 1);
            case 'mov': return undefinedOrToFixed(this.mov, 3);
            case 'iome': return undefinedOrToFixed(this.iome, 3);
            case 'file_size': return formatBytes(this.file_size);
        }
        return undefined;
    }
}

function parseLevel(level: string | CustomLevel): VideoLevel {
    if (typeof level !== 'string') return level;
    const customLevel = CustomLevel.fromCode(level);
    return customLevel ?? level as MS_Level;
}

export function groupVideosByDate(videos: VideoAbstract[], attr: 'upload_time' | 'end_time' = 'upload_time'): Map<string, VideoAbstract[]> {
    const result = new Map<string, VideoAbstract[]>();

    videos.forEach((video) => {
        let date = video[attr];
        date ??= video.upload_time; // fallback to upload_time if end_time is not available
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

export function isStandardVideo(video: VideoAbstract): video is StandardVideoAbstract {
    return isStandardLevel(video.level);
}
