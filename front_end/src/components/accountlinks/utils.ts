import { Platform } from '@/utils/common/accountLinkPlatforms';

export interface AccountSaolei {
    id: number;
    name: string;
    update_time: string;
    total_views?: number;

    beg_count?: number;
    int_count?: number;
    exp_count?: number;

    b_t_ms?: number;
    i_t_ms?: number;
    e_t_ms?: number;

    b_b_cent?: number;
    i_b_cent?: number;
    e_b_cent?: number;
}

export const AccountSaoleiDefault: AccountSaolei = {
    id: 0,
    name: '',
    update_time: '1970-01-01T00:00:00.000Z',
    total_views: 0,

    beg_count: 0,
    int_count: 0,
    exp_count: 0,

    b_t_ms: 999990,
    i_t_ms: 999990,
    e_t_ms: 999990,

    b_b_cent: 0,
    i_b_cent: 0,
    e_b_cent: 0,
};

export interface AccountMSGames {
    id: number;
    name: string;
    update_time: string;

    local_name: string;
    joined: Date;
}

export const AccountMSGamesDefault: AccountMSGames = {
    id: 0,
    name: '',
    update_time: '1970-01-01T00:00:00.000Z',

    local_name: '',
    joined: new Date(0),
};

export interface AccountWoM {
    id: number;
    update_time: string;

    trophy?: number;
    experience?: number;
    honour?: number;

    minecoin?: number;
    gem?: number;
    coin?: number;
    arena_ticket?: number;
    equipment?: number;
    part?: number;

    arena_point?: number;
    max_difficulty?: number;
    win?: number;
    last_season?: number;

    b_t_ms?: number;
    i_t_ms?: number;
    e_t_ms?: number;

    b_ioe?: number;
    i_ioe?: number;
    e_ioe?: number;

    b_mastery?: number;
    i_mastery?: number;
    e_mastery?: number;

    b_winstreak?: number;
    i_winstreak?: number;
    e_winstreak?: number;
}

export const AccountWoMDefault: AccountWoM = {
    id: 0,
    update_time: '1970-01-01T00:00:00.000Z',
};

export interface AccountLink {
    platform: Platform;
    identifier: string;
    verified: boolean;
    data?: AccountSaolei | AccountMSGames | AccountWoM;
}
