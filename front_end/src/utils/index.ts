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

import { ComponentCustomProperties } from "vue";
export function approve(proxy: ComponentCustomProperties & Record<string, any>, id: number) {
    proxy.$axios.get('video/approve?ids=['+id+']').then(function (response) {
        console.log(response.data)
    }).catch()
}
