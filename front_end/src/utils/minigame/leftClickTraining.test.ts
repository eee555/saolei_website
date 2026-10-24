import { describe, expect, it } from 'vitest';

import { leftClickModes, LeftClickTraining } from './leftClickTraining';

function findCells(board: number[][], value: number) {
    return board.flatMap((row, r) => row.flatMap((cell, c) => (cell === value ? [{ row: r, column: c }] : [])));
}

describe('left-click training', () => {
    it.each([
        ['left-click-b-50-v1', 8, 8, 32, 32],
        ['left-click-b-75-v1', 8, 8, 48, 16],
        ['left-click-b-87.5-v1', 8, 8, 56, 8],
        ['left-click-i-50-v1', 16, 16, 128, 128],
        ['left-click-i-75-v1', 16, 16, 192, 64],
        ['left-click-i-87.5-v1', 16, 16, 224, 32],
        ['left-click-e-50-v1', 16, 30, 240, 240],
        ['left-click-e-75-v1', 16, 30, 360, 120],
        ['left-click-e-87.5-v1', 16, 30, 420, 60],
    ] as const)('%s has the exact shape and visible mine count', (key, rows, columns, mines, safe) => {
        const mode = leftClickModes.find((item) => item.rankingKey === key);
        if (mode === undefined) throw new Error(`Missing training mode: ${key}`);
        const game = new LeftClickTraining(mode, () => 0.5);
        expect(game.board).toHaveLength(rows);
        expect(game.board.every((row) => row.length === columns)).toBe(true);
        expect(findCells(game.board, 16)).toHaveLength(mines);
        expect(findCells(game.board, 10)).toHaveLength(safe);
        expect(game.remainingSafe).toBe(safe);
        expect(game.phase).toBe('ready');
        expect(game.elapsedMs(100000)).toBe(0);
    });

    it('starts on the first accepted action, opens one cell and ignores repeated cells', () => {
        const game = new LeftClickTraining(leftClickModes[0], () => 0.5);
        const safe = findCells(game.board, 10);
        const mines = findCells(game.board, 16);
        const [first] = safe;
        expect(game.elapsedMs(5000)).toBe(0);
        expect(game.phase).toBe('ready');
        expect(game.trigger(first.row, first.column, 6000)).toBe(true);
        expect(game.phase).toBe('playing');
        expect(game.elapsedMs(6000)).toBe(0);
        expect(game.elapsedMs(6500)).toBe(500);
        expect(game.remainingSafe).toBe(31);
        expect(findCells(game.board, 0)).toEqual([first]);
        expect(findCells(game.board, 16)).toEqual(mines);
        expect(game.trigger(first.row, first.column, 7000)).toBe(false);
        expect(game.remainingSafe).toBe(31);
        expect(game.elapsedMs(7500)).toBe(1500);
    });

    it('does not start or change the game for coordinates outside a cell', () => {
        const game = new LeftClickTraining(leftClickModes[0], () => 0.5);
        const original = game.board;
        for (const [row, column] of [[-1, 0], [0, -1], [8, 0], [0, 8], [0.5, 1], [NaN, 0]]) {
            expect(game.trigger(row, column, 6000)).toBe(false);
        }
        expect(game.phase).toBe('ready');
        expect(game.elapsedMs(99999)).toBe(0);
        expect(game.board).toEqual(original);
    });

    it.each([false, true])('freezes a loss and stops accepting input (first click: %s)', (firstClick) => {
        const game = new LeftClickTraining(leftClickModes[0], () => 0.5);
        const [safe] = findCells(game.board, 10);
        const [mine] = findCells(game.board, 16);
        if (!firstClick) game.trigger(safe.row, safe.column, 1000);
        game.trigger(mine.row, mine.column, 1500);
        expect(game.phase).toBe('lost');
        expect(game.board[mine.row][mine.column]).toBe(15);
        expect(game.elapsedMs(99999)).toBe(firstClick ? 0 : 500);
        expect(game.trigger(safe.row, safe.column, 100000)).toBe(false);
        expect(game.remainingSafe).toBe(firstClick ? 32 : 31);
    });

    it.each([0, 1234.6])('freezes a positive rounded millisecond result on the last safe cell (%s ms)', (duration) => {
        const game = new LeftClickTraining(leftClickModes[2], () => 0.5);
        const safe = findCells(game.board, 10);
        safe.forEach(({ row, column }, index) => {
            game.trigger(row, column, index === safe.length - 1 ? 8000 + duration : 8000);
        });
        expect(game.phase).toBe('won');
        expect(game.remainingSafe).toBe(0);
        expect(findCells(game.board, 0)).toHaveLength(8);
        expect(game.elapsedMs(99999)).toBe(Math.max(1, Math.round(duration)));
        const [mine] = findCells(game.board, 16);
        expect(game.trigger(mine.row, mine.column, 100000)).toBe(false);
        expect(game.phase).toBe('won');
    });

    it('keeps instances and display copies independent', () => {
        const first = new LeftClickTraining(leftClickModes[0], () => 0.5);
        const second = new LeftClickTraining(leftClickModes[0], () => 0.5);
        const [safe] = findCells(first.board, 10);
        first.trigger(safe.row, safe.column, 1000);
        const copy = first.board;
        copy[safe.row][safe.column] = 16;
        expect(first.board[safe.row][safe.column]).toBe(0);
        expect(second.board[safe.row][safe.column]).toBe(10);
        expect(second.phase).toBe('ready');
        expect(second.remainingSafe).toBe(32);
    });
});
