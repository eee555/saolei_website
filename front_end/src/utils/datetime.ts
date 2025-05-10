export const fullDay = 86400000 as const;
export const fullWeek = 604800000 as const;
export const monthNameShort = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] as const;

/**
 * 获取指定日期所在周的起始时间
 * @param {Date} date - 需要计算周起始时间的日期
 * @returns {number} - 返回指定日期所在周的起始时间的时间戳
 */
export function getWeekTime(date: Date) {
    return date.getTime() - date.getDay() * fullDay;
}

/**
 * 将日期对象转换为ISO格式的本地日期字符串
 * @param {Date} date - 日期对象
 * @returns {string} - ISO格式的本地日期字符串，例如 "2022-01-01"
 */
export function toISODateString(date: Date) {
    return date.getFullYear() + '-' + (date.getMonth() + 1).toString().padStart(2, '0') + '-' + date.getDate().toString().padStart(2, '0');
}

export function toISODateTimeString(date: Date) {
    return date.getFullYear() + '-' + (date.getMonth() + 1).toString().padStart(2, '0') + '-' + date.getDate().toString().padStart(2, '0') + ' ' +
        date.getHours().toString().padStart(2, '0') + ':' + date.getMinutes().toString().padStart(2, '0') + ':' +
        date.getSeconds().toString().padStart(2, '0');
}
