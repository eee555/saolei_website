import type { ClassicMouseAction } from '../classicMouse';

import { TrainingClock } from './clock';
import type { TrainingPhase } from './clock';
import { trainingLevels } from './levels';

export const flagChordModes = [
    { ...trainingLevels[0], total: 4 },
    { ...trainingLevels[1], total: 15 },
] as const;
export type FlagChordMode = typeof flagChordModes[number];

export interface FlagChordQuestion {
    readonly row: number;
    readonly column: number;
    readonly neighbors: readonly number[];
    readonly mine: number;
}

function questionPositions(rows: number, columns: number, total: number, random: () => number): { row: number; column: number }[] {
    const positions: { row: number; column: number }[] = [];
    const place = (row: number, column: number, height: number, width: number, count: number): void => {
        if (count === 1) {
            positions.push({ row: row + 1 + Math.floor(random() * (height - 2)), column: column + 1 + Math.floor(random() * (width - 2)) });
            return;
        }
        // Only split where both regions can accommodate their assigned question counts.
        const splits: { byRows: boolean; offset: number; firstCapacity: number; secondCapacity: number }[] = [];
        for (const byRows of [true, false]) {
            const length = byRows ? height : width;
            const across = Math.floor((byRows ? width : height) / 3);
            for (let offset = 3; offset <= length - 3; offset++) {
                const firstCapacity = Math.floor(offset / 3) * across;
                const secondCapacity = Math.floor((length - offset) / 3) * across;
                if (firstCapacity + secondCapacity >= count) splits.push({ byRows, offset, firstCapacity, secondCapacity });
            }
        }
        const { byRows, offset, firstCapacity, secondCapacity } = splits[Math.floor(random() * splits.length)];
        const minimum = Math.max(1, count - secondCapacity);
        const maximum = Math.min(firstCapacity, count - 1);
        const firstCount = minimum + Math.floor(random() * (maximum - minimum + 1));
        if (byRows) {
            place(row, column, offset, width, firstCount);
            place(row + offset, column, height - offset, width, count - firstCount);
        } else {
            place(row, column, height, offset, firstCount);
            place(row, column + offset, height, width - offset, count - firstCount);
        }
    };
    place(0, 0, rows, columns, total);
    return positions;
}

export class FlagChordTraining {
    public readonly mode: FlagChordMode;
    public readonly questions: readonly FlagChordQuestion[];
    public phase: TrainingPhase = 'ready';
    private readonly owners = new Map<number, FlagChordQuestion>();
    private readonly flags = new Set<number>();
    private readonly completed = new Set<FlagChordQuestion>();
    private readonly clock = new TrainingClock();
    private exploded: number | null = null;

    public constructor(mode: FlagChordMode, random: () => number = Math.random, initialBoard?: number[][]) {
        this.mode = mode;
        const positions = initialBoard === undefined ? questionPositions(mode.rows, mode.columns, mode.total, random) : initialBoard.flatMap((row, r) => row.flatMap((value, c) => (value === 1 ? [{ row: r, column: c }] : [])));
        this.questions = positions.map(({ row, column }) => {
            const neighbors: number[] = [];
            for (let r = row - 1; r <= row + 1; r++) {
                for (let c = column - 1; c <= column + 1; c++) {
                    if (r !== row || c !== column) neighbors.push(r * mode.columns + c);
                }
            }
            const mine = initialBoard === undefined ? neighbors[Math.floor(random() * neighbors.length)] : neighbors.find((cell) => initialBoard[Math.floor(cell / mode.columns)][cell % mode.columns] === 16);
            if (mine === undefined) throw new Error('Missing mine in flag-and-chord question');
            const question: FlagChordQuestion = { row, column, neighbors, mine };
            this.owners.set(row * mode.columns + column, question);
            for (const cell of neighbors) this.owners.set(cell, question);
            return question;
        });
    }

    public get remaining(): number {
        return this.mode.total - this.completed.size;
    }

    public get board(): number[][] {
        return Array.from({ length: this.mode.rows }, (_row, row) => Array.from({ length: this.mode.columns }, (_column, column) => {
            const index = row * this.mode.columns + column;
            const question = this.owners.get(index);
            if (question === undefined) return 0;
            if (row === question.row && column === question.column) return 1;
            if (index === this.exploded) return 15;
            if (this.flags.has(index)) return this.phase === 'lost' && index !== question.mine ? 14 : 11;
            if (index === question.mine) return 16;
            return this.completed.has(question) ? 0 : 10;
        }));
    }

    public elapsedMs(now: number): number {
        return this.clock.elapsedMs(now);
    }

    public act(action: ClassicMouseAction, row: number, column: number, now: number): boolean {
        if (this.phase === 'won' || this.phase === 'lost' || action === 'left') return false;
        if (!Number.isInteger(row) || !Number.isInteger(column) || row < 0 || column < 0 || row >= this.mode.rows || column >= this.mode.columns) return false;
        const index = row * this.mode.columns + column;
        const question = this.owners.get(index);
        if (question === undefined || this.completed.has(question)) return false;
        const center = row === question.row && column === question.column;
        if (action === 'right') {
            if (center) return false;
            if (!this.flags.delete(index)) {
                this.flags.add(index);
                this.clock.start(now);
                this.phase = 'playing';
            }
            return true;
        }
        if (!center || question.neighbors.filter((cell) => this.flags.has(cell)).length !== 1) return false;
        if (!this.flags.has(question.mine)) {
            this.exploded = question.mine;
            this.phase = 'lost';
            this.clock.finish(now, false);
        } else {
            this.completed.add(question);
            if (this.remaining === 0) {
                this.phase = 'won';
                this.clock.finish(now, true);
            }
        }
        return true;
    }
}
