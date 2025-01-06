// Credit: ChatGPT
export function range(start: number, end: number, step: number = 1): number[] {
    if (step <= 0) {
        throw new Error("Step must be greater than 0.");
    }
    const result: number[] = [];
    for (let i = start; step > 0 ? i <= end : i >= end; i += step) {
        result.push(i);
    }
    return result;
}