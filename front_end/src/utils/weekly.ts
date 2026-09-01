import { MS_Mode } from './ms_const';
import { TournamentParticipant } from './tournaments';

export type WeeklyVideoScore = [number, number];

const DEFAULT_WEEKLY_EXPERT_TIME = 240000;
const DEFAULT_WEEKLY_INTERMEDIATE_TIME = 60000;

export const WeeklyTournamentFormat = {
    Classic: 'c',
} as const;

export type WeeklyTournamentFormat = typeof WeeklyTournamentFormat[keyof typeof WeeklyTournamentFormat];

export function isWeeklyClassicScoreMode(mode: MS_Mode): boolean {
    return ([MS_Mode.Standard, MS_Mode.NoFlag] as readonly MS_Mode[]).includes(mode);
}

function makeDefaultScores(count: number, score: number): WeeklyVideoScore[] {
    return Array.from({ length: count }, () => [0, score]);
}

export class WeeklyParticipant extends TournamentParticipant {
    public classic_et: WeeklyVideoScore[] = makeDefaultScores(2, DEFAULT_WEEKLY_EXPERT_TIME);
    public classic_it: WeeklyVideoScore[] = makeDefaultScores(5, DEFAULT_WEEKLY_INTERMEDIATE_TIME);
    public classic_score = DEFAULT_WEEKLY_EXPERT_TIME * 2 + DEFAULT_WEEKLY_INTERMEDIATE_TIME * 5;

    public constructor(init?: Partial<WeeklyParticipant>) {
        super(init);
        Object.assign(this, init);
    }

    public get classic_e_sum(): number {
        return this.classic_et.reduce((sum, score) => sum + score[1], 0);
    }

    public get classic_i_sum(): number {
        return this.classic_it.reduce((sum, score) => sum + score[1], 0);
    }
}
