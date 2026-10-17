import type { BoardExportState } from './boardExportFrame';

export function composeBoardFrame(context: CanvasRenderingContext2D, region: { x: number; y: number }, state: Pick<BoardExportState, 'input' | 'globalOpacity' | 'probabilityOpacity' | 'traceOpacity'>, cellSize: number, layers: Partial<Record<'background' | 'foreground' | 'probability' | 'mouseTrace', CanvasImageSource>>, global?: CanvasImageSource, cursor?: { image: CanvasImageSource; x: number; y: number; size: number }): void {
    context.save();
    try {
        context.resetTransform();
        context.globalAlpha = 1;
        context.globalCompositeOperation = 'source-over';
        context.clearRect(0, 0, context.canvas.width, context.canvas.height);
        context.translate(-region.x, -region.y);
        context.beginPath();
        context.rect(0, 0, Math.max(...state.input.board.map((row) => row.length)) * cellSize, state.input.board.length * cellSize);
        context.clip();
        const draw = (source: CanvasImageSource | undefined, opacity: number) => {
            if (source === undefined) return;
            context.globalAlpha = opacity;
            context.drawImage(source, 0, 0);
        };
        draw(layers.background, 1);
        draw(global, state.globalOpacity);
        draw(layers.foreground, 1);
        draw(layers.probability, state.probabilityOpacity);
        draw(layers.mouseTrace, state.traceOpacity);
        if (cursor !== undefined) {
            context.globalAlpha = 1;
            context.drawImage(cursor.image, cursor.x, cursor.y, cursor.size, cursor.size);
        }
    } finally {
        context.restore();
    }
}
