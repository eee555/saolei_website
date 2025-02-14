export const fullDay = 86400000 as const;
export const fullWeek = 604800000 as const;
export const monthNameShort = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] as const;

export function getWeekTime(date: Date) {
    return date.getTime() - date.getDay() * fullDay;
}

export function toISODateString(date: Date) {
    return date.getFullYear() + '-' + (date.getMonth() + 1).toString().padStart(2, '0') + '-' + date.getDate().toString().padStart(2, '0');
}