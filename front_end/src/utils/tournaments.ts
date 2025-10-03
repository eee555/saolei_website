import { toISODateTimeString } from './datetime';
import { TournamentState, TournamentSeries } from './ms_const';

export class Tournament {
    public id: number;
    public name: string;
    public description?: string | Record<string, string>;
    public startDate?: Date;
    public endDate?: Date;
    public hostId: number;
    public hostName: string;
    public state: TournamentState;
    public series: TournamentSeries;

    constructor(info: any) {
        if (info.id) this.id = info.id;
        else this.id = 0;

        if (info.name) this.name = info.name;
        else this.name = '';

        this.description = info.description;

        if (info.startDate) this.startDate = new Date(info.startDate);
        else if (info.start_time) this.startDate = new Date(info.start_time);

        if (info.endDate) this.endDate = new Date(info.endDate);
        else if (info.end_time) this.endDate = new Date(info.end_time);

        if (info.hostId) this.hostId = info.hostId;
        else if (info.host_id) this.hostId = info.host_id;
        else this.hostId = 0;

        if (info.hostName) this.hostName = info.hostName;
        else if (info.host_realname) this.hostName = info.host_realname;
        else this.hostName = '';

        if (info.state) this.state = info.state;
        else this.state = TournamentState.Pending;

        if (info.series) this.series = info.series;
        else this.series = TournamentSeries.Unknown;
    }

    /**
     * 根据提供的本地化标识符获取对应的描述文本
     *
     * @param local - 本地化标识符，用于指定要获取的描述文本的语言或地区
     * @returns 返回匹配的描述文本。如果找不到匹配项，则返回空字符串
     *
     * @remarks
     * 该方法会检查description属性是否存在，如果不存在则直接返回空字符串。
     * 如果description是字符串类型，则直接返回该字符串。
     * 对于对象类型的description，会尝试使用提供的local参数作为键查找对应的值。
     * 如果找不到匹配项，会使用Tournament.localFallback方法进行回退查找。
     *
     * @example
     */
    public getLocalDescription(local: string) {
        if (!this.description) return '';
        if (typeof this.description === 'string') return this.description;
        let _local = local as string | undefined;
        while (_local && !this.description[_local]) {
            _local = Tournament.localFallback(_local);
        }
        if (_local === undefined) return '';
        return this.description[_local];
    }

    public static localFallback(local: string | undefined) {
        if (local === undefined) return undefined;
        if (local === 'zh') return undefined;
        if (local.startsWith('zh')) return 'zh';
        if (local === 'en') return undefined;
        return 'en';
    }

    public displayStartTime() {
        if (!this.startDate) return '';
        return toISODateTimeString(this.startDate);
    }

    public displayEndTime() {
        if (!this.endDate) return '';
        return toISODateTimeString(this.endDate);
    }
}
