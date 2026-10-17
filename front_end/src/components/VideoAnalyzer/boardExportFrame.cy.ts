import BoardCursorLayer from './BoardCursorLayer.vue';
import { createBoardFrameRenderer } from './boardExportFrame';
import type { BoardExportState, ExportCursor } from './boardExportFrame';

describe('native board frame rendering', () => {
    for (const shape of ['dot', 'windows'] as const) {
        it(`composes real layers and a ${shape} SVG cursor, including cursor movement and crop`, () => {
            cy.mount(BoardCursorLayer, { props: { position: null, cellSize: 16, shape, size: 32 } }).then(async ({ wrapper }) => {
                const layer = wrapper.vm as { snapshot: (position?: { rowIndex: number; columnIndex: number }, cellSize?: number) => ExportCursor | null };
                expect(layer.snapshot()).to.eq(null);
                const cursor = layer.snapshot({ rowIndex: 0.5, columnIndex: 0.5 }, 32);
                if (cursor === null) throw new Error('Expected a cursor snapshot');
                expect(cursor.x).to.eq(shape === 'windows' ? 13 : 0);
                expect(cursor.y).to.eq(shape === 'windows' ? 14 : 0);
                const state: BoardExportState = {
                    input: { board: [[10, 10], [10, 10]],
                        size: 32,
                        layers: {
                            probability: { board: [[0.5, 0.5], [0.5, 0.5]], color: () => 'red' },
                            mouseTrace: { events: [{ row: 1.5, column: 0.25, action: 'mv', state: 'uu' }, { row: 1.5, column: 1.75, action: 'mv', state: 'uu' }], opacity: 0.5 },
                        } },
                    globalBoard: [[1, 2], [3, 4]],
                    globalOpacity: 0.4,
                    probabilityOpacity: 0.5,
                    traceOpacity: 0.6,
                    cursor: null,
                };
                const output = document.createElement('canvas');
                output.width = output.height = 64;
                const context = output.getContext('2d');
                if (context === null) throw new Error('Expected a canvas context');
                const session = createBoardFrameRenderer(() => state, new AbortController().signal);
                const sample = shape === 'dot' ? { x: 16, y: 16, rgb: [255, 223, 0] } : { x: 19, y: 26, rgb: [255, 255, 255] };
                const pixel = (x: number, y: number) => Array.from(context.getImageData(x, y, 1, 1).data);
                try {
                    await session.render(context, { x: 0, y: 0 });
                    const base = pixel(sample.x, sample.y);
                    expect(base[3]).to.eq(255);
                    state.cursor = cursor;
                    await session.render(context, { x: 0, y: 0 });
                    expect(pixel(sample.x, sample.y).slice(0, 3)).to.deep.eq(sample.rgb);
                    state.cursor = { ...cursor, x: cursor.x + 32 };
                    await session.render(context, { x: 0, y: 0 });
                    expect(pixel(sample.x, sample.y)).to.deep.eq(base);
                    expect(pixel(sample.x + 32, sample.y).slice(0, 3)).to.deep.eq(sample.rgb);
                    output.width = 32;
                    await session.render(context, { x: 32, y: 0 });
                    expect(pixel(sample.x, sample.y).slice(0, 3)).to.deep.eq(sample.rgb);
                } finally {
                    session.close();
                    output.width = output.height = 0;
                }
            });
        });
    }
});
