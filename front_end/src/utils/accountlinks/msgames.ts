export interface AccountMSGamesResponse {
    id: number;
    parent: number;
    update_time: string;
    name: string;
    local_name: string;
    joined: string | null;
}

export class AccountMSGames {
    public id = 0;
    public name = '';
    public update_time = new Date(0);
    public local_name = '';
    public joined = new Date(0);

    public constructor(data?: AccountMSGamesResponse) {
        if (data === undefined) return;

        this.id = data.id;
        this.name = data.name;
        this.update_time = new Date(data.update_time);
        this.local_name = data.local_name;
        this.joined = data.joined === null ? new Date(0) : new Date(data.joined);
    }
}
