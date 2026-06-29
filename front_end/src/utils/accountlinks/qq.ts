export interface AccountQQResponse {
    id: number;
    parent: number;
}

export class AccountQQ {
    public id = 0;
    public parent = 0;

    public constructor(data?: AccountQQResponse) {
        if (data === undefined) return;

        this.id = data.id;
        this.parent = data.parent;
    }
}
