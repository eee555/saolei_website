import { Platform } from '@/utils/common/accountLinkPlatforms';
import { DjangoTaskResultStatus } from '@/utils/common/structInterface';
import { MS_Level } from '@/utils/ms_const';

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

export interface SaoleiVideo {
    id: number;
    user__id: number;
    level: MS_Level;
    timems: number;
    bv: number;
    nf: boolean;
    upload_time: string;
    import_video__id: number;
    import_task__status: DjangoTaskResultStatus;
}

export interface SaoleiImportSummary {
    bulk_task_status: DjangoTaskResultStatus;
    total: number;
    old_imported: number;
    new_total: number;
    new_ready: number;
    new_success: number;
    new_failed: number;
    new_connection: number;
}

export const SaoleiImportSummaryDefault: SaoleiImportSummary = {
    bulk_task_status: 'NULL',
    total: 0,
    old_imported: 0,
    new_total: 0,
    new_ready: 0,
    new_success: 0,
    new_failed: 0,
    new_connection: 0,
};
