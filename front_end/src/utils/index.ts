import { ComponentCustomProperties } from 'vue';

type DeepMutable<T> = T extends readonly (infer U)[]
    ? DeepMutable<U>[]                     // 数组递归
    : T extends object
        ? { -readonly [K in keyof T]: DeepMutable<T[K]> }  // 对象递归移除 readonly
        : T;                                  // 基础类型原样

/**
 * 创建对象的深拷贝副本，确保返回的对象是完全可变的
 * @param obj - 需要进行深拷贝的对象
 * @returns 返回一个深拷贝后的可变对象
 */
export function deepMutableCopy<T>(obj: T): DeepMutable<T> {
    // 使用structuredClone方法进行深拷贝
    // 并将结果断言为DeepMutable类型
    return structuredClone(obj) as DeepMutable<T>;
}

export type EnumMap<T extends string | number | symbol, V> = { [K in T]: V; };

/**
 * 根据键数组和默认值，创建一个包含所有键且值均为默认值的对象。
 * 返回类型精确到键的联合类型，确保所有键都存在。
 */
export function createEnumMap<T extends readonly string[], V>(
    keys: T,
    defaultValue: V,
): { [K in T[number]]: V } {
    return Object.fromEntries(keys.map((key) => [key, defaultValue])) as {
        [K in T[number]]: V;
    };
}

export function to_fixed_n(input: string | number | undefined, to_fixed: number): string | number | undefined {
    // 返回保留to_fixed位小数的字符串，四舍六入五取双
    if (input === undefined) {
        return input;
    }
    if (to_fixed <= 0) {
        return input;
    }
    if (typeof (input) == 'string') {
        return parseFloat(input).toFixed(to_fixed);
    }
    return (input as number).toFixed(to_fixed);
}

// 毫秒的整数到字符串秒的小数
export function ms_to_s(ms: number | undefined): string {
    if (ms === undefined) return '-';
    return `${Math.floor(ms / 1000)}.${(ms % 1000 + '').padStart(3, '0')}`;
}
export function cs_to_s(cs: number): string {
    return `${Math.floor(cs / 100)}.${(cs % 100 + '').padStart(2, '0')}`;
}

export function simple_formatter(f: Function) {
    return (row: any, col: any, value: any, _index: any) => f(value);
}
export async function approve(proxy: ComponentCustomProperties & Record<string, any>, id: number) {
    let status;
    await proxy.$axios.get('video/approve?ids=[' + id + ']').then(function (response: any) {
        const data = response.data;
        if (data.length != 1) {
            console.log(data);
            throw new Error('Unexpected error');
        }
        status = data[0];
    }).catch();
    return status;
}

export async function freeze(proxy: ComponentCustomProperties & Record<string, any>, id: number) {
    let status;
    await proxy.$axios.get('video/freeze?ids=[' + id + ']').then(function (response: any) {
        const data = response.data;
        if (data.length != 1) {
            console.log(data);
            throw new Error('Unexpected error');
        }
        status = data[0];
    }).catch();
    return status;
}

// Credit: ChatGPT
export function deepCopy<T>(obj: T): T {
    if (obj === null || typeof obj !== 'object') {
        return obj;
    }

    if (obj instanceof Array) {
        const copy: any[] = [];
        for (let i = 0; i < obj.length; i++) {
            copy[i] = deepCopy(obj[i]);
        }
        return copy as unknown as T;
    }

    if (obj instanceof Object) {
        const copy: { [key: string]: any } = {};
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                copy[key] = deepCopy(obj[key]);
            }
        }
        return copy as T;
    }

    throw new Error('Unable to copy object! Its type isn\'t supported.');
}

export function defaultFilterMethod(value: any, row: any, column: any) {
    return row[column.property] === value;
}

export function sleep(ms: number) {
    return new Promise((resolve) => setTimeout(() => resolve(ms), ms));
}
