import { getInsertIndex, isAscending, isDescending } from "./arrays";

export class PiecewiseColorScheme {
    private colors: string[];
    private thresholds: number[];
    private ascending: boolean;

    constructor(colors: string[], thresholds: number[]) {
        this.colors = colors;
        this.thresholds = thresholds;
        if (isAscending(thresholds)) {
            this.ascending = true;
        } else if (isDescending(thresholds)) {
            this.ascending = false;
        } else {
            throw new Error("Thresholds must be either ascending or descending");
        }
    }

    public getColor(value: number): string {
        const index = getInsertIndex(this.thresholds, value, this.ascending);
        return this.colors[index];
    }
}