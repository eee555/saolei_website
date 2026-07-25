type FormDataValue = string | number | boolean | Blob;

export function Dict2FormData(data: Record<string, FormDataValue>): FormData {
    const form = new FormData();
    for (const [key, value] of Object.entries(data)) {
        form.append(key, value instanceof Blob ? value : String(value));
    }
    return form;
}
