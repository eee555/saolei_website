export interface AccountWoMResponse {
    id: number;
    parent: number;
    update_time: string;
    trophy: number | null;
    experience: number | null;
    honour: number | null;
    minecoin: number | null;
    gem: number | null;
    coin: number | null;
    arena_ticket: number | null;
    equipment: number | null;
    part: number | null;
    arena_point: number | null;
    max_difficulty: number | null;
    win: number | null;
    last_season: number | null;
    b_t_ms: number | null;
    i_t_ms: number | null;
    e_t_ms: number | null;
    b_ioe: number | null;
    i_ioe: number | null;
    e_ioe: number | null;
    b_mastery: number | null;
    i_mastery: number | null;
    e_mastery: number | null;
    b_winstreak: number | null;
    i_winstreak: number | null;
    e_winstreak: number | null;
}

export class AccountWoM {
    public id = 0;
    public update_time = new Date(0);
    public trophy?: number;
    public experience?: number;
    public honour?: number;
    public minecoin?: number;
    public gem?: number;
    public coin?: number;
    public arena_ticket?: number;
    public equipment?: number;
    public part?: number;
    public arena_point?: number;
    public max_difficulty?: number;
    public win?: number;
    public last_season?: number;
    public b_t_ms?: number;
    public i_t_ms?: number;
    public e_t_ms?: number;
    public b_ioe?: number;
    public i_ioe?: number;
    public e_ioe?: number;
    public b_mastery?: number;
    public i_mastery?: number;
    public e_mastery?: number;
    public b_winstreak?: number;
    public i_winstreak?: number;
    public e_winstreak?: number;

    public constructor(data?: AccountWoMResponse) {
        if (data === undefined) return;

        this.id = data.id;
        this.update_time = new Date(data.update_time);
        this.trophy = data.trophy ?? undefined;
        this.experience = data.experience ?? undefined;
        this.honour = data.honour ?? undefined;
        this.minecoin = data.minecoin ?? undefined;
        this.gem = data.gem ?? undefined;
        this.coin = data.coin ?? undefined;
        this.arena_ticket = data.arena_ticket ?? undefined;
        this.equipment = data.equipment ?? undefined;
        this.part = data.part ?? undefined;
        this.arena_point = data.arena_point ?? undefined;
        this.max_difficulty = data.max_difficulty ?? undefined;
        this.win = data.win ?? undefined;
        this.last_season = data.last_season ?? undefined;
        this.b_t_ms = data.b_t_ms ?? undefined;
        this.i_t_ms = data.i_t_ms ?? undefined;
        this.e_t_ms = data.e_t_ms ?? undefined;
        this.b_ioe = data.b_ioe ?? undefined;
        this.i_ioe = data.i_ioe ?? undefined;
        this.e_ioe = data.e_ioe ?? undefined;
        this.b_mastery = data.b_mastery ?? undefined;
        this.i_mastery = data.i_mastery ?? undefined;
        this.e_mastery = data.e_mastery ?? undefined;
        this.b_winstreak = data.b_winstreak ?? undefined;
        this.i_winstreak = data.i_winstreak ?? undefined;
        this.e_winstreak = data.e_winstreak ?? undefined;
    }
}
