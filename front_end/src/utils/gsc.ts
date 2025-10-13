import { GSCDefaults } from './ms_const';

export interface GSCInfo {
    id: number;
    start_time?: Date;
    end_time?: Date;
    token?: string;
}

export interface GSCParticipant {
    user__id: number;
    user__realname: string;
    bt1st: number;
    bt20th: number;
    bt20sum: number;
    it1st: number;
    it12th: number;
    it12sum: number;
    et1st: number;
    et5th: number;
    et5sum: number;
}

export const GSCParticipantDefault: GSCParticipant = {
    user__id: 0,
    user__realname: '',
    bt1st: GSCDefaults.bt,
    bt20th: GSCDefaults.bt,
    bt20sum: GSCDefaults.bt * 20,
    it1st: GSCDefaults.it,
    it12th: GSCDefaults.it,
    it12sum: GSCDefaults.it * 12,
    et1st: GSCDefaults.et,
    et5th: GSCDefaults.et,
    et5sum: GSCDefaults.et * 5,
} as const;
