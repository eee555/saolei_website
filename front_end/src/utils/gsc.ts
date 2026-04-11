import { GSCDefaults } from './ms_const';

export interface GSCInfo {
    id: number;
    start_time?: Date;
    end_time?: Date;
    token?: string;
}

export class GSCParticipant {
    id: number = 0;
    user__id: number = 0;
    user__realname: string = '';
    bt1st: number = GSCDefaults.bt;
    bt20th: number = GSCDefaults.bt;
    bt20sum: number = GSCDefaults.bt * 20;
    it1st: number = GSCDefaults.it;
    it12th: number = GSCDefaults.it;
    it12sum: number = GSCDefaults.it * 12;
    et1st: number = GSCDefaults.et;
    et5th: number = GSCDefaults.et;
    et5sum: number = GSCDefaults.et * 5;

    constructor(init?: Partial<GSCParticipant>) {
        Object.assign(this, init);
    }

    get sum_tbest() {
        return this.bt1st + this.it1st + this.et1st;
    }

    get sum_tedge() {
        return this.bt20th + this.it12th + this.et5th;
    }

    get sum_tsum() {
        return this.bt20sum + this.it12sum + this.et5sum;
    }
}
