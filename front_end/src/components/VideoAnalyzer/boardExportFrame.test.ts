import type { BoardRenderInput } from '@putianyi888/vue3-minesweeper-board';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { createBoardFrameRenderer } from './boardExportFrame';
import type { BoardExportState } from './boardExportFrame';

const sdk = vi.hoisted(() => ({ create: vi.fn(), render: vi.fn(), destroy: vi.fn(), decode: vi.fn(), serialize: vi.fn() }));
vi.mock('@putianyi888/vue3-minesweeper-board', () => ({ createBoardRenderer: sdk.create }));

function frame(names = ['background', 'foreground', 'probability', 'mouseTrace']) {
    return { layers: Object.fromEntries(names.map((name) => [name, { name }])) as unknown as Record<string, HTMLCanvasElement>, width: 33, height: 33, cellSize: 16.4, released: false, release: vi.fn() };
}

function setup() {
    const state: BoardExportState = { input: { board: [[10, 1], [0, 10]], size: 16.4 }, globalBoard: [[1, 1], [0, -1]], globalOpacity: 0.4, probabilityOpacity: 0.5, traceOpacity: 0.6, cursor: null };
    const calls: { source: unknown; alpha: number; args: number[] }[] = [];
    const contextMocks = {
        save: vi.fn(),
        restore: vi.fn(),
        resetTransform: vi.fn(),
        clearRect: vi.fn(),
        translate: vi.fn(),
        beginPath: vi.fn(),
        rect: vi.fn(),
        clip: vi.fn(),
    };
    const context = { canvas: { width: 16, height: 17 },
        globalAlpha: 1,
        ...contextMocks,
        drawImage(this: { globalAlpha: number }, source: unknown, ...args: number[]) {
            calls.push({ source, alpha: this.globalAlpha, args });
        } } as unknown as CanvasRenderingContext2D;
    const controller = new AbortController();
    const global = frame(['foreground']);
    const current = frame();
    sdk.render.mockImplementation((input: BoardRenderInput) => Promise.resolve(input.layers?.background === false ? global : current));
    const session = createBoardFrameRenderer(() => state, controller.signal);
    return { state, calls, context, contextMocks, controller, global, current, session };
}

beforeEach(() => {
    vi.resetAllMocks();
    sdk.create.mockReturnValue({ render: sdk.render, destroy: sdk.destroy });
    sdk.decode.mockResolvedValue(undefined);
    sdk.serialize.mockReturnValue('<svg />');
    vi.stubGlobal('Image', class {
        public src = '';
        public decode = sdk.decode;
    });
    vi.stubGlobal('XMLSerializer', class {
        public serializeToString = sdk.serialize;
    });
});
afterEach(() => vi.unstubAllGlobals());

describe('board frame composition', () => {
    it('reads explicit export time synchronously and disposes the private parser once on cancellation', async () => {
        const { state, context } = setup();
        const controller = new AbortController();
        const read = vi.fn(() => state);
        const dispose = vi.fn<() => void>();
        const session = createBoardFrameRenderer(read, controller.signal, dispose);
        const pending = session.render(context, { x: 0, y: 0 }, 1250);
        expect(read).toHaveBeenCalledExactlyOnceWith(1250);
        await pending;
        controller.abort();
        session.close();
        expect(dispose).toHaveBeenCalledOnce();
    });

    it('preserves layer order, opacity and fractional cell geometry, and renders directly into the crop', async () => {
        const { calls, context, contextMocks, session, global, current } = setup();
        try {
            await session.render(context, { x: 16, y: 16 });
            expect(calls.map((call) => call.source)).toEqual([current.layers.background, global.layers.foreground, current.layers.foreground, current.layers.probability, current.layers.mouseTrace]);
            expect(calls.map((call) => call.alpha)).toEqual([1, 0.4, 1, 0.5, 0.6]);
            expect(contextMocks.clearRect).toHaveBeenCalledWith(0, 0, 16, 17);
            expect(contextMocks.translate).toHaveBeenCalledWith(-16, -16);
            expect(contextMocks.rect).toHaveBeenCalledWith(0, 0, 32.8, 32.8);
            expect(current.release).toHaveBeenCalledOnce();
            expect(global.release).not.toHaveBeenCalled();
            await session.render(context, { x: 0, y: 0 });
            expect(sdk.render).toHaveBeenCalledTimes(3);
        } finally {
            session.close();
        }
        session.close();
        expect(global.release).toHaveBeenCalledOnce();
        expect(sdk.destroy).toHaveBeenCalledOnce();
        await expect(session.render(context, { x: 0, y: 0 })).rejects.toThrow('Board renderer is closed');
    });

    it('does not request disabled layers or invent a cursor position', async () => {
        const { state, calls, context, session } = setup();
        state.globalBoard = null;
        state.input.layers = { probability: false, mouseTrace: false };
        sdk.render.mockResolvedValue(frame(['background', 'foreground']));
        try {
            await session.render(context, { x: 0, y: 0 });
            expect(sdk.render).toHaveBeenCalledExactlyOnceWith(state.input);
            expect(calls).toHaveLength(2);
            expect(sdk.decode).not.toHaveBeenCalled();
        } finally {
            session.close();
        }
    });

    it('decodes a cursor only once, removes its DOM transform and draws it last at the updated position', async () => {
        const { state, calls, context, session } = setup();
        const removeProperty = vi.fn();
        const clone = { style: { removeProperty } };
        state.cursor = { svg: { cloneNode: vi.fn(() => clone) } as unknown as SVGSVGElement, x: 4, y: 8, size: 32 };
        try {
            await session.render(context, { x: 0, y: 0 });
            expect(removeProperty).toHaveBeenCalledWith('transform');
            expect(sdk.serialize).toHaveBeenCalledWith(clone);
            expect(calls.at(-1)).toMatchObject({ alpha: 1, args: [4, 8, 32, 32] });
            state.cursor.x = 20;
            await session.render(context, { x: 0, y: 0 });
            expect(sdk.decode).toHaveBeenCalledOnce();
            expect(calls.at(-1)?.args).toEqual([20, 8, 32, 32]);
        } finally {
            session.close();
        }
    });

    it('propagates draw failures while releasing the frame and restoring the context', async () => {
        const { context, contextMocks, session, current } = setup();
        context.drawImage = () => {
            throw new Error('Draw failed');
        };
        try {
            await expect(session.render(context, { x: 0, y: 0 })).rejects.toThrow('Draw failed');
            expect(current.release).toHaveBeenCalledOnce();
            expect(contextMocks.restore).toHaveBeenCalledOnce();
        } finally {
            session.close();
        }
    });

    it('destroys a pending renderer on abort without drawing or leaking returned frames', async () => {
        const { context, session, controller, current, calls } = setup();
        sdk.render.mockImplementationOnce(() => {
            controller.abort();
            return Promise.reject(new Error('Destroyed'));
        });
        await expect(session.render(context, { x: 0, y: 0 })).rejects.toThrow('Destroyed');
        session.close();
        expect(sdk.destroy).toHaveBeenCalledOnce();
        expect(calls).toHaveLength(0);
        expect(current.release).not.toHaveBeenCalled();
    });

    it('releases a completed frame if cancellation occurs before it can be composed', async () => {
        const { state, context, session, controller, current, calls } = setup();
        state.globalBoard = null;
        sdk.render.mockImplementationOnce(() => {
            controller.abort();
            return Promise.resolve(current);
        });
        await expect(session.render(context, { x: 0, y: 0 })).rejects.toMatchObject({ name: 'AbortError' });
        session.close();
        expect(sdk.destroy).toHaveBeenCalledOnce();
        expect(current.release).toHaveBeenCalledOnce();
        expect(calls).toHaveLength(0);
    });

    it('releases a late global frame when cancellation races with the first render', async () => {
        const { context, session, controller, global } = setup();
        sdk.render.mockImplementationOnce(() => {
            controller.abort();
            return Promise.resolve(global);
        });
        await expect(session.render(context, { x: 0, y: 0 })).rejects.toMatchObject({ name: 'AbortError' });
        session.close();
        expect(sdk.destroy).toHaveBeenCalledOnce();
        expect(global.release).toHaveBeenCalledOnce();
        expect(sdk.render).toHaveBeenCalledOnce();
    });

    it('releases the frame and reports SVG decoding failure rather than exporting a missing cursor', async () => {
        const { state, context, session, current } = setup();
        state.cursor = { svg: { cloneNode: () => ({ style: { removeProperty: vi.fn() } }) } as unknown as SVGSVGElement, x: 0, y: 0, size: 32 };
        sdk.decode.mockRejectedValue(new Error('SVG decode failed'));
        try {
            await expect(session.render(context, { x: 0, y: 0 })).rejects.toThrow('SVG decode failed');
            expect(current.release).toHaveBeenCalledOnce();
        } finally {
            session.close();
        }
    });
});
