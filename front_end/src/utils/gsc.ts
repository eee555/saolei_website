
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
