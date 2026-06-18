export function getLastDigit(num: number): number {
    return num % 10;
}

export function setLastDigit(num: number, digit: number): number {
    return num - getLastDigit(num) + digit;
}

export function clamp(value: number, min: number, max: number): number {
    return Math.min(Math.max(value, min), max);
}
