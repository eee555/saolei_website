import type { DjangoTaskResultStatus } from '../common/structInterface';
import type { MS_Level } from '../ms_const';

export interface AccountSaoleiResponse {
    id: number;
    parent: number;
    update_time: string;
    video_import_task: number | null;
    name: string;
    total_views: number;
    beg_count: number;
    int_count: number;
    exp_count: number;
    b_t_ms: number | null;
    i_t_ms: number | null;
    e_t_ms: number | null;
    s_t_ms: number | null;
    b_b_cent: number | null;
    i_b_cent: number | null;
    e_b_cent: number | null;
    s_b_cent: number | null;
}

export class AccountSaolei {
    public id = 0;
    public name = '';
    public update_time = new Date(0);
    public total_views = 0;
    public beg_count = 0;
    public int_count = 0;
    public exp_count = 0;
    public b_t_ms = 999990;
    public i_t_ms = 999990;
    public e_t_ms = 999990;
    public b_b_cent = 0;
    public i_b_cent = 0;
    public e_b_cent = 0;

    public constructor(data?: AccountSaoleiResponse) {
        if (data === undefined) return;

        this.id = data.id;
        this.name = data.name;
        this.update_time = new Date(data.update_time);
        this.total_views = data.total_views;
        this.beg_count = data.beg_count;
        this.int_count = data.int_count;
        this.exp_count = data.exp_count;
        this.b_t_ms = data.b_t_ms ?? this.b_t_ms;
        this.i_t_ms = data.i_t_ms ?? this.i_t_ms;
        this.e_t_ms = data.e_t_ms ?? this.e_t_ms;
        this.b_b_cent = data.b_b_cent ?? this.b_b_cent;
        this.i_b_cent = data.i_b_cent ?? this.i_b_cent;
        this.e_b_cent = data.e_b_cent ?? this.e_b_cent;
    }

    public get sum_t_ms(): number {
        return this.b_t_ms + this.i_t_ms + this.e_t_ms;
    }

    public get sum_b_cent(): number {
        return this.b_b_cent + this.i_b_cent + this.e_b_cent;
    }
}

export interface SaoleiVideoRaw {
    id: number;
    user__id: number;
    level: MS_Level;
    timems: number;
    bv: number;
    nf: boolean;
    upload_time: string;
    import_video__id: number | null;
    import_task__status: DjangoTaskResultStatus | null;
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
