
export function binaryStringToUint8Array(binaryString: string): Uint8Array {
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i) & 0xff;
    }
    return bytes;
}
