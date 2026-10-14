export type MineracerAccountLinkStatus = 'pending' | 'confirmed' | 'expired' | 'failed';

export interface AccountMineracerResponse {
    id: string;
    parent: number;
    update_time: string;
}

export class AccountMineracer {
    public id = '';
    public update_time = new Date(0);

    public constructor(data?: AccountMineracerResponse) {
        if (data === undefined) return;

        this.id = data.id;
        this.update_time = new Date(data.update_time);
    }
}

export interface MineracerAccountLinkSessionResponse {
    session_id: string;
    status: MineracerAccountLinkStatus;
    user_code: string;
    verification_uri: string;
    verification_uri_complete: string;
    expires_at: string;
    next_poll_at: string | null;
    remote_userid: string;
    error_category: string;
}

export class MineracerAccountLinkSession {
    public session_id = '';
    public status: MineracerAccountLinkStatus = 'pending';
    public user_code = '';
    public verification_uri = '';
    public verification_uri_complete = '';
    public expires_at = new Date(0);
    public next_poll_at?: Date;
    public remote_userid = '';
    public error_category = '';

    public constructor(data?: MineracerAccountLinkSessionResponse) {
        if (data === undefined) return;

        this.session_id = data.session_id;
        this.status = data.status;
        this.user_code = data.user_code;
        this.verification_uri = data.verification_uri;
        this.verification_uri_complete = data.verification_uri_complete;
        this.expires_at = new Date(data.expires_at);
        this.next_poll_at = data.next_poll_at === null ? undefined : new Date(data.next_poll_at);
        this.remote_userid = data.remote_userid;
        this.error_category = data.error_category;
    }
}
