import { createBoardRenderer } from '@putianyi888/vue3-minesweeper-board';
import type { BoardRenderFrame, BoardRenderInput } from '@putianyi888/vue3-minesweeper-board';

import { composeBoardFrame } from './boardExportComposition';

export interface ExportCursor {
    svg: SVGSVGElement;
    x: number;
    y: number;
    size: number;
}

export interface BoardExportState {
    input: BoardRenderInput;
    globalBoard: number[][] | null;
    globalOpacity: number;
    probabilityOpacity: number;
    traceOpacity: number;
    cursor: ExportCursor | null;
}

export interface BoardFrameRenderer {
    render: (context: CanvasRenderingContext2D, region: { x: number; y: number }, replayMs?: number) => Promise<void>;
    close: () => void;
}

export function createBoardFrameRenderer(getState: (replayMs: number) => BoardExportState, signal: AbortSignal, dispose?: () => void): BoardFrameRenderer {
    signal.throwIfAborted();
    const renderer = createBoardRenderer();
    let globalFrame: BoardRenderFrame<HTMLCanvasElement> | undefined;
    let cursorImage: HTMLImageElement | undefined;
    let closed = false;

    function close() {
        if (closed) return;
        closed = true;
        signal.removeEventListener('abort', close);
        globalFrame?.release();
        renderer.destroy();
        if (cursorImage) cursorImage.src = '';
        dispose?.();
    }
    signal.addEventListener('abort', close, { once: true });

    return {
        close,
        async render(context, region, replayMs = 0) {
            signal.throwIfAborted();
            if (closed) throw new Error('Board renderer is closed');
            const state = getState(replayMs);
            if (state.globalBoard !== null && globalFrame === undefined) {
                const global = await renderer.render({ board: state.input.board,
                    size: state.input.size,
                    layers: { background: false, foreground: { board: state.globalBoard } } });
                if (signal.aborted || closed) {
                    global.release();
                    signal.throwIfAborted();
                    throw new Error('Board renderer is closed');
                }
                globalFrame = global;
            }
            const frame = await renderer.render(state.input);
            try {
                signal.throwIfAborted();
                if (closed) throw new Error('Board renderer is closed');
                if (state.cursor !== null && cursorImage === undefined) {
                    // Shape/size are frozen during export. Only rasterize the small SVG once.
                    cursorImage = new Image();
                    const svg = state.cursor.svg.cloneNode(true) as SVGSVGElement;
                    svg.style.removeProperty('transform');
                    cursorImage.src = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(new XMLSerializer().serializeToString(svg))}`;
                    await cursorImage.decode();
                }
                signal.throwIfAborted();
                if (closed) throw new Error('Board renderer is closed');
                composeBoardFrame(context, region, state, frame.cellSize, frame.layers, state.globalBoard === null ? undefined : globalFrame?.layers.foreground, state.cursor !== null && cursorImage !== undefined ? { ...state.cursor, image: cursorImage } : undefined);
            } finally {
                frame.release();
            }
        },
    };
}
