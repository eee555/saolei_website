export type TrainingPhase = 'ready' | 'playing' | 'won' | 'lost';

/** 仅记录操作时间戳；动画帧、失焦和显示控件均不改变成绩。 */
export class TrainingClock {
    private startedAt: number | null = null;
    private finishedAt: number | null = null;
    private successful = false;

    public start(now: number): void {
        this.startedAt ??= now;
    }

    public finish(now: number, successful: boolean): void {
        this.finishedAt = now;
        this.successful = successful;
    }

    public elapsedMs(now: number): number {
        if (this.startedAt === null) return 0;
        return Math.max(this.successful ? 1 : 0, Math.round((this.finishedAt ?? now) - this.startedAt));
    }
}
