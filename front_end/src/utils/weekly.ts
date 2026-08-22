export type WeeklyVideoScore = [number, number];

const DEFAULT_WEEKLY_EXPERT_TIME = 240000;
const DEFAULT_WEEKLY_INTERMEDIATE_TIME = 60000;

function makeDefaultScores(count: number, timems: number): WeeklyVideoScore[] {
    return Array.from({ length: count }, () => [0, timems]);
}

export class WeeklyParticipant {
    public id = 0;
    public user_id: number | null = null;
    public start_time: string | Date | null = null;
    public end_time: string | Date | null = null;
    public rank: number | null = null;
    public rank_score = 0;
    public classic_et: WeeklyVideoScore[] = makeDefaultScores(2, DEFAULT_WEEKLY_EXPERT_TIME);
    public classic_it: WeeklyVideoScore[] = makeDefaultScores(5, DEFAULT_WEEKLY_INTERMEDIATE_TIME);
    public classic_score = DEFAULT_WEEKLY_EXPERT_TIME * 2 + DEFAULT_WEEKLY_INTERMEDIATE_TIME * 5;

    public constructor(init?: Partial<WeeklyParticipant>) {
        Object.assign(this, init);
    }

    public get classic_e_sum(): number {
        return this.classic_et.reduce((sum, score) => sum + score[1], 0);
    }

    public get classic_i_sum(): number {
        return this.classic_it.reduce((sum, score) => sum + score[1], 0);
    }
}
