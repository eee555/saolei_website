// Credit: ChatGPT
/**
 * 生成一个 range
 * @param start
 * @param end 
 * @param step 
 * @returns start:step:end
 */
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

// Credit: DeepSeek
/**
 * 接收一个数组或者迭代器，返回最大值
 * @param iter 
 * @returns 
 */
export function maximum(iter: number[] | MapIterator<number>): number {
    const arr = Array.isArray(iter) ? iter : Array.from(iter);

    if (arr.length === 0) {
        return -Infinity;
    }

    let max = arr[0];
    for (let i = 1; i < arr.length; i++) {
        if (arr[i] > max) {
            max = arr[i];
        }
    }

    return max;
}

/**
 * 接收一个数组或者迭代器，返回最小值
 * @param iter 
 * @returns 
 */
export function minimum(iter: number[] | MapIterator<number>): number {
    const arr = Array.isArray(iter) ? iter : Array.from(iter);

    if (arr.length === 0) {
        return Infinity;
    }

    let min = arr[0];
    for (let i = 1; i < arr.length; i++) {
        if (arr[i] < min) {
            min = arr[i];
        }
    }

    return min;
}

// Credit: ChatGPT
export function getInsertIndex(sortedArray: number[], value: number, isAscending: boolean): number {
    // Determine the insertion point using binary search
    let low = 0;
    let high = sortedArray.length;

    while (low < high) {
        const mid = Math.floor((low + high) / 2);

        if (isAscending) {
            if (sortedArray[mid] < value) low = mid + 1;
            else high = mid;
        } else {
            if (sortedArray[mid] > value) low = mid + 1;
            else high = mid;
        }
    }

    return low;
}

/**
 * 判断数组是否是升序的
 * @param arr 
 * @returns 
 */
export function isAscending(arr: number[]): boolean {
    for (let i = 0; i < arr.length - 1; i++) {
        if (arr[i] > arr[i + 1]) {
            return false;
        }
    }
    return true;
}

/**
 * 判断数组是否是降序的
 * @param arr 
 * @returns 
 */
export function isDescending(arr: number[]): boolean {
    for (let i = 0; i < arr.length - 1; i++) {
        if (arr[i] < arr[i + 1]) {
            return false;
        }
    }
    return true;
}