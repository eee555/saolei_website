// \u2028: Line Separator
// \u2029: Paragraph Separator
export const containsControl = /[\x00-\x1F\x7F-\x9F\u2028\u2029]/;

// credit: ChatGPT
export function stringifyWithLineWrap(
    obj: any,
    maxLineLength: number = 80,
    indent: number = 2,
): string {
    const INDENTATION = ' '.repeat(indent);

    function processValue(value: any, currentIndent: string): string {
        if (Array.isArray(value)) {
            let line = '[';
            const lines: string[] = [];
            for (let i = 0; i < value.length; i++) {
                const itemStr = JSON.stringify(value[i]);
                if (line.length + itemStr.length + 2 > maxLineLength) {
                    lines.push(line.trimEnd() + ',');
                    line = currentIndent + INDENTATION + itemStr;
                } else {
                    line += (line === '[' ? '' : ', ') + itemStr;
                }
            }
            if (line !== '[') lines.push(line.trimEnd());
            return lines.join('\n') + ']';
        } else if (typeof value === 'object' && value !== null) {
            const keys = Object.keys(value);
            let result = '{\n';
            for (const key of keys) {
                const keyValue = JSON.stringify(key) + ': ' + processValue(value[key], currentIndent + INDENTATION);
                result += currentIndent + INDENTATION + keyValue + ',\n';
            }
            result = result.replace(/,\n$/, '\n'); // Remove trailing comma
            result += currentIndent + '}';
            return result;
        } else {
            return JSON.stringify(value);
        }
    }

    return processValue(obj, '');
}

export function countRows(str: string): number {
    return str.split('\n').length;
}

export function formatBytes(bytes: number, decimals: number = 2): string {
    if (bytes === 0) return '0 B';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}
