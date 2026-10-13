import type { ReplayVideo } from './replayParser';

export interface CursorPosition {
    rowIndex: number;
    columnIndex: number;
}

export function readReplayCursor(replay: ReplayVideo): CursorPosition | null {
    const cursor = replay.x_y;
    try {
        const pixelSize = replay.pix_size;
        const rowIndex = cursor.y / pixelSize;
        const columnIndex = cursor.x / pixelSize;
        return pixelSize > 0 && Number.isFinite(rowIndex) && Number.isFinite(columnIndex)
            && rowIndex >= 0 && rowIndex <= replay.row && columnIndex >= 0 && columnIndex <= replay.column
            ? { rowIndex, columnIndex }
            : null;
    } finally {
        cursor.free();
    }
}
