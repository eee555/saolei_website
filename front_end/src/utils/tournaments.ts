import { toDate, toISODateTimeString } from './datetime';
import { TournamentSeries, TournamentState } from './ms_const';

export interface TournamentParticipant {
    id: number;
    user__id: number;
    user__realname: string;
}

type LocalizedString = string | Partial<Record<string, string>>;

interface TournamentInfo {
    [key: string]: unknown;
    id?: number;
    name?: LocalizedString;
    description?: LocalizedString;
    startDate?: string | Date | null;
    start_time?: string | Date | null;
    endDate?: string | Date | null;
    end_time?: string | Date | null;
    hostId?: number;
    host_id?: number;
    hostName?: string;
    host_realname?: string;
    state?: TournamentState;
    series?: TournamentSeries;
}

export class Tournament {
    public id: number;
    public name: LocalizedString;
    public description?: LocalizedString;
    public startDate?: Date;
    public endDate?: Date;
    public hostId: number;
    public hostName: string;
    public state: TournamentState;
    public series: TournamentSeries;

    public constructor(info: TournamentInfo) {
        this.id = info.id ?? 0;
        this.name = info.name ?? '';
        this.description = info.description;

        this.startDate = toDate(info.startDate) ?? toDate(info.start_time);
        this.endDate = toDate(info.endDate) ?? toDate(info.end_time);

        this.hostId = info.hostId ?? info.host_id ?? 0;
        this.hostName = info.hostName ?? info.host_realname ?? '';
        this.state = info.state ?? TournamentState.Pending;
        this.series = info.series ?? TournamentSeries.Unknown;
    }

    public static localFallback(local: string | undefined): 'zh' | 'en' | undefined {
        if (local === undefined) return undefined;
        if (local === 'zh') return undefined;
        if (local.startsWith('zh')) return 'zh';
        if (local === 'en') return undefined;
        return 'en';
    }

    public static getLocalString(message: LocalizedString, local?: string): string {
        if (typeof message === 'string') return message;
        let _local = local;
        while (_local !== undefined) {
            const nextMessage = message[_local];
            if (nextMessage !== undefined) return nextMessage;
            _local = Tournament.localFallback(_local);
        }
        return '';
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
    public getLocalDescription(local: string): string {
        if (this.description === undefined) return '';
        return Tournament.getLocalString(this.description, local);
    }

    public getLocalName(local?: string): string {
        return Tournament.getLocalString(this.name, local);
    }

    public displayStartTime(): string {
        if (!this.startDate) return '';
        return toISODateTimeString(this.startDate);
    }

    public displayEndTime(): string {
        if (!this.endDate) return '';
        return toISODateTimeString(this.endDate);
    }
}
