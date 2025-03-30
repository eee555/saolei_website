export function Dict2FormData(data: Record<string, any>): FormData {
    const form = new FormData();
    for (const [key, value] of Object.entries(data)) {
        form.append(key, value);
    }
    return form
}