// \u2028: Line Separator
// \u2029: Paragraph Separator
export const containsControl = /[\x00-\x1F\x7F-\x9F\u2028\u2029]/;
