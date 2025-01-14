export const fullDay = 86400000 as const;
export const fullWeek = 604800000 as const;
export const monthNameShort = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] as const;

export function getWeekTime(date:Date) {
    return date.getTime() - date.getDay() * fullDay;
}