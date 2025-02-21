export function getLastDigit(num: number): number {
    return num % 10;
}

export function setLastDigit(num: number, digit: number): number {
    return num - getLastDigit(num) + digit;
}