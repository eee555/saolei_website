export function to_fixed_n(input: string | number | undefined, to_fixed: number): string | number | undefined {
    // 返回保留to_fixed位小数的字符串，四舍六入五取双
    if (input === undefined) {
        return input;
    }
    if (to_fixed <= 0) {
        return input;
    }
    if (typeof (input) == "string") {
        return parseFloat(input).toFixed(to_fixed);
    }
    return (input as number).toFixed(to_fixed);
}

// 毫秒的整数到字符串秒的小数
export function ms_to_s(ms: number): string {
    return `${Math.floor(ms / 1000)}.${(ms % 1000 + "").padStart(3, '0')}`;
}

export function simple_formatter(f: Function): Function {
    return (row: any, col: any, value: any, index: any) => f(value)
}

import { ComponentCustomProperties } from "vue";
export async function approve(proxy: ComponentCustomProperties & Record<string, any>, id: number) {
    var status;
    await proxy.$axios.get('video/approve?ids=[' + id + ']').then(function (response) {
        const data = response.data;
        if (data.length != 1) {
            console.log(data)
            throw new Error('Unexpected error')
        }
        status = data[0]
    }).catch()
    return status
}

export async function freeze(proxy: ComponentCustomProperties & Record<string, any>, id: number) {
    var status;
    await proxy.$axios.get('video/freeze?ids=[' + id + ']').then(function (response) {
        const data = response.data;
        if (data.length != 1) {
            console.log(data)
            throw new Error('Unexpected error')
        }
        status = data[0]
    }).catch()
    return status
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
