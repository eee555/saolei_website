import { GSCDefaults } from './ms_const';

export interface GSCInfo {
    id: number;
    start_time?: Date;
    end_time?: Date;
    token?: string;
}

export class GSCParticipant {
    public id = 0;
    public user__id = 0;
    public user__realname = '';
    public bt1st: number = GSCDefaults.bt;
    public bt20th: number = GSCDefaults.bt;
    public bt20sum: number = GSCDefaults.bt * 20;
    public it1st: number = GSCDefaults.it;
    public it12th: number = GSCDefaults.it;
    public it12sum: number = GSCDefaults.it * 12;
    public et1st: number = GSCDefaults.et;
    public et5th: number = GSCDefaults.et;
    public et5sum: number = GSCDefaults.et * 5;

    public constructor(init?: Partial<GSCParticipant>) {
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
