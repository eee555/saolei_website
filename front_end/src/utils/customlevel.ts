export type CustomLevelCode = `c${number}_${number}_${number}`;

export class CustomLevel {
    public readonly row: number;
    public readonly column: number;
    public readonly mine: number;

    public constructor(row: number, column: number, mine: number);
    public constructor(value: string);
    public constructor(rowOrValue: number | string, column?: number, mine?: number) {
        if (typeof rowOrValue === 'string') {
            const parsed = CustomLevel.parse(rowOrValue);
            if (!parsed) throw new Error(`Invalid custom level: ${rowOrValue}`);
            this.row = parsed.row;
            this.column = parsed.column;
            this.mine = parsed.mine;
            return;
        }

        if (column === undefined || mine === undefined) throw new Error('Custom level requires row, column and mine');
        const row = rowOrValue;
        this.row = row;
        this.column = column;
        this.mine = mine;
    }

    public get code(): CustomLevelCode {
        return `c${this.row}_${this.column}_${this.mine}`;
    }

    public get density(): number {
        return this.mine / this.row / this.column;
    }

    public get boardKey(): string {
        return `${this.row}x${this.column}x${this.mine}`;
    }

    /**
     * 将后端返回的`level`字符串转换为`CustomLevel`，形式为`c{h}_{w}_{m}`
     */
    public static fromCode(code: string): CustomLevel | undefined {
        return CustomLevel.parse(code) ? new CustomLevel(code) : undefined;
    }

    private static parse(value: string): { row: number; column: number; mine: number } | undefined {
        const match = (/^(?:c(\d+)_(\d+)_(\d+)|(\d+)x(\d+)\/(\d+))$/).exec(value);
        if (!match) return undefined;
        return {
            row: Number(match[1] ?? match[4]),
            column: Number(match[2] ?? match[5]),
            mine: Number(match[3] ?? match[6]),
        };
    }

    public compare(other: CustomLevel): number {
        return this.row - other.row || this.column - other.column || this.mine - other.mine;
    }

    public matches(row: number, column: number, mine: number): boolean {
        return this.row === row && this.column === column && this.mine === mine;
    }

    public toString(): string {
        return `${this.row}x${this.column}/${this.mine}`;
    }
}

export const DensityCustomLevelConfigs = [
    new CustomLevel(8, 8, 40),
    new CustomLevel(16, 16, 100),
    new CustomLevel(16, 30, 150),
    new CustomLevel(24, 30, 200),
] as const;

const DensityCustomLevelByBoard = new Map<string, CustomLevel>(
    DensityCustomLevelConfigs.map((config) => [config.boardKey, config]),
);

export function getDensityCustomLevelByBoard(row: number, column: number, mine: number): CustomLevel | undefined {
    return DensityCustomLevelByBoard.get(`${row}x${column}x${mine}`);
}

export function isDensityCustomLevel(row: number, column: number, mine: number): boolean {
    return getDensityCustomLevelByBoard(row, column, mine) !== undefined;
}
