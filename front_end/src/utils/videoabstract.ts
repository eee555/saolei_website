import { MS_Level } from './ms_const';
import * as echarts from 'echarts/core';

export interface VideoAbstractInfo {
    id: number,
    upload_time: Date,
    level: MS_Level,
    mode: string,
    timems: number,
    bv: number,
    state: string,
    software: string,
}

export type getStat_stat = 'time' | 'bvs' | 'timems' | 'bv' | 'qg' | 'rqp';

export class VideoAbstract {
    public id: number | null;
    public upload_time: Date;
    public level: MS_Level;
    public mode: string;
    public timems: number;
    public bv: number;
    public state: string;
    public software: string;

    constructor(info: VideoAbstractInfo) {
        this.id = info.id;
        this.upload_time = info.upload_time;
        this.level = info.level;
        this.mode = info.mode;
        this.timems = info.timems;
        this.bv = info.bv;
        this.state = info.state;
        this.software = info.software;
    }

    public time() {
        return this.timems / 1000;
    }

    public bvs() {
        return this.bv/this.time();
    }

    public qg() {
        return this.time()^1.7/this.bv;
    }

    public rqp() {
        return this.time()*(this.time()-1)/this.bv;
    }

    public getStat(stat: getStat_stat) {
        switch (stat) {
            case 'time': return this.time();
            case 'bvs': return this.bvs();
            case 'timems': return this.timems;
            case 'bv': return this.bv;
            case 'qg': return this.qg();
            case 'rqp': return this.rqp();
        }
    }

    public tooltipFormatter(t: any) {
        // t is the localization API from i18n
        return `${t('common.prop.upload_time')}: ${this.upload_time} <br>
        ${t('common.level.'+this.level)} ${this.bv}Bv = ${this.time().toFixed(3)} * ${this.bvs().toFixed(3)}`
    }
}

export const getData = (year: string | number, level: Array<string>) => {
    const data = [] as Array<[string, number]>;
    const date = +echarts.number.parseDate(year + '-01-01');
    const end = +echarts.number.parseDate(year + '-12-31');
    // let thiscount = 0;
    // for (let time = date; time <= end; time += 3600 * 24 * 1000) {
    //     data.push([
    //         echarts.time.format(time, '{yyyy}-{MM}-{dd}', false),
    //         0
    //     ]);
    // }
    // for (let video of videos) {
    //     if (!level.includes(video.level)) {
    //         continue;
    //     }
    //     let video_date = +echarts.number.parseDate(video.upload_time);
    //     let date_index = Math.floor((video_date - date) / (3600 * 24 * 1000));
    //     if (date_index >= 0 && date_index < data.length) {
    //         data[date_index][1] += 1;
    //         thiscount += 1;
    //     }
    // }
    return data;
}