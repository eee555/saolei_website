export type CustomLevelCode = `c${number}_${number}_${number}`;

export class CustomLevel {
    public readonly row: number;
    public readonly column: number;
    public readonly mine: number;
    public readonly value: CustomLevelCode;

    public constructor(row: number, column: number, mine: number) {
        this.row = row;
        this.column = column;
        this.mine = mine;
        this.value = `c${row}_${column}_${mine}`;
    }

    public get code(): CustomLevelCode {
        return this.value;
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
        const match = (/^c(\d+)_(\d+)_(\d+)$/).exec(code);
        if (!match) return undefined;
        return new CustomLevel(Number(match[1]), Number(match[2]), Number(match[3]));
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
    new CustomLevel(8, 8, 20),
    new CustomLevel(8, 8, 24),
    new CustomLevel(8, 8, 28),
    new CustomLevel(8, 8, 32),
    new CustomLevel(8, 8, 36),
    new CustomLevel(8, 8, 40),
    new CustomLevel(16, 16, 64),
    new CustomLevel(16, 16, 80),
    new CustomLevel(16, 16, 96),
    new CustomLevel(16, 16, 112),
    new CustomLevel(16, 16, 128),
    new CustomLevel(16, 30, 120),
    new CustomLevel(16, 30, 144),
    new CustomLevel(16, 30, 168),
    new CustomLevel(16, 30, 192),
    new CustomLevel(24, 30, 180),
    new CustomLevel(24, 30, 216),
    new CustomLevel(24, 30, 252),
    new CustomLevel(48, 64, 777),
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
