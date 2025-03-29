/**
 * ArrayUtils 类提供了一系列用于处理数组的静态方法。
 */
export class ArrayUtils {
    /**
     * 生成一个从start到end的数字序列，步长为step。
     * @param start 序列的起始值
     * @param end 序列的结束值
     * @param step 序列的步长，默认为1
     * @returns 一个包含从start到end的数字序列的数组
     */
    static range(start: number, end: number, step: number = 1): number[] {
        const result: number[] = [];
        for (let i = start; step > 0 ? i <= end : i >= end; i += step) {
            result.push(i);
        }
        return result;
    }

    /**
     * 返回给定迭代器中的最大值。
     * 
     * @param iter - 一个数字数组或一个数字迭代器。
     * @returns 迭代器中的最大值，如果迭代器为空，则返回负无穷大。
     */
    static maximum(iter: number[] | MapIterator<number>): number {
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
     * 计算给定迭代器中的最小值。
     * @param iter - 一个数字数组或Map迭代器。
     * @returns 迭代器中的最小值，如果迭代器为空则返回Infinity。
     */
    static minimum(iter: number[] | MapIterator<number>): number {
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

    /**
     * 获取插入索引
     * @param sortedArray 已排序的数组
     * @param value 要插入的值
     * @param isAscending 是否升序
     * @returns 插入索引
     */
    static getInsertIndex(sortedArray: number[], value: number, isAscending: boolean): number {
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
     * 检查数组是否按升序排列
     * @param arr 要检查的数组
     * @returns 如果数组按升序排列，则返回 true；否则返回 false
     */
    static isAscending(arr: number[]): boolean {
        for (let i = 0; i < arr.length - 1; i++) {
            if (arr[i] > arr[i + 1]) {
                return false;
            }
        }
        return true;
    }

    /**
     * 判断数组是否按降序排列
     * @param arr 要检查的数组
     * @returns 如果数组按降序排列，则返回 true；否则返回 false
     */
    static isDescending(arr: number[]): boolean {
        for (let i = 0; i < arr.length - 1; i++) {
            if (arr[i] < arr[i + 1]) {
                return false;
            }
        }
        return true;
    }

    static empty<T>(arr: T[]): void {
        arr.splice(0, arr.length);
        return;
    }

    static isEmpty<T>(arr: T[]): boolean {
        return arr.length === 0;
    }
}
