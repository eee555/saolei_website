import { describe, expect, it } from 'vitest';

import { flagChordModes, FlagChordTraining } from './flagChordTraining';

function flag(game: FlagChordTraining, index: number, now: number) {
    return game.act('right', Math.floor(index / game.mode.columns), index % game.mode.columns, now);
}

describe('flag-and-chord training', () => {
    it.each(flagChordModes)('$key generates its fixed number of nonoverlapping, single-mine questions', (mode) => {
        for (const pattern of [[0], [0.37], [0.99], [0.13, 0.81, 0.4, 0.97, 0.21]]) {
            let draw = 0;
            const game = new FlagChordTraining(mode, () => pattern[draw++ % pattern.length]);
            const { board } = game;
            expect(game.questions).toHaveLength(mode.total);
            expect(board).toHaveLength(mode.rows);
            expect(board.every((row) => row.length === mode.columns)).toBe(true);
            const occupied = game.questions.flatMap((question) => {
                expect(question.row).toBeGreaterThanOrEqual(1);
                expect(question.row).toBeLessThan(mode.rows - 1);
                expect(question.column).toBeGreaterThanOrEqual(1);
                expect(question.column).toBeLessThan(mode.columns - 1);
                expect(question.neighbors).toHaveLength(8);
                expect(question.neighbors).toContain(question.mine);
                expect(board[question.row][question.column]).toBe(1);
                expect(board[Math.floor(question.mine / mode.columns)][question.mine % mode.columns]).toBe(16);
                return [question.row * mode.columns + question.column, ...question.neighbors];
            });
            expect(new Set(occupied).size).toBe(mode.total * 9);
            expect(board.flat().filter((cell) => cell === 1)).toHaveLength(mode.total);
            expect(board.flat().filter((cell) => cell === 16)).toHaveLength(mode.total);
            expect(board.flat().filter((cell) => cell === 10)).toHaveLength(mode.total * 7);
            expect(board.flat().filter((cell) => cell === 0)).toHaveLength(mode.rows * mode.columns - mode.total * 9);
            expect(game.remaining).toBe(mode.total);
            expect(game.phase).toBe('ready');
            expect(game.elapsedMs(100000)).toBe(0);
        }
    });

    it.each(flagChordModes)('$key randomizes actual question positions', (mode) => {
        const first = new FlagChordTraining(mode, () => 0);
        const second = new FlagChordTraining(mode, () => 0.99);
        const centers = (game: FlagChordTraining) => game.questions.map(({ row, column }) => `${row},${column}`).sort();
        expect(centers(first)).not.toEqual(centers(second));
    });

    it('ignores left clicks, empty regions, numbers used as flags, and invalid coordinates before timing', () => {
        const game = new FlagChordTraining(flagChordModes[0], () => 0.37);
        const [question] = game.questions;
        const original = game.board;
        original.forEach((row, r) => {
            row.forEach((value, c) => {
                expect(game.act('left', r, c, 1000)).toBe(false);
                if (value === 0) expect(game.act('right', r, c, 1000)).toBe(false);
            });
        });
        expect(game.act('right', question.row, question.column, 1000)).toBe(false);
        expect(game.act('chord', question.row, question.column, 1000)).toBe(false);
        for (const [r, c] of [[-1, 0], [0, -1], [8, 0], [0, 8], [0.5, 0], [NaN, 0]]) expect(game.act('right', r, c, 1000)).toBe(false);
        expect(game.board).toEqual(original);
        expect(game.phase).toBe('ready');
        expect(game.elapsedMs(99999)).toBe(0);
    });

    it('times the first flag, allows correction, and requires exactly one flag for a chord', () => {
        const game = new FlagChordTraining(flagChordModes[0], () => 0.37);
        const [question] = game.questions;
        const [safe] = question.neighbors.filter((cell) => cell !== question.mine);
        flag(game, safe, 1000);
        expect(game.phase).toBe('playing');
        expect(game.elapsedMs(1500)).toBe(500);
        flag(game, safe, 1600);
        expect(game.act('chord', question.row, question.column, 1700)).toBe(false);
        flag(game, question.mine, 1800);
        flag(game, safe, 1900);
        expect(game.act('chord', question.row, question.column, 2000)).toBe(false);
        flag(game, safe, 2100);
        expect(game.elapsedMs(2200)).toBe(1200);
        expect(game.act('chord', question.row, question.column, 2300)).toBe(true);
        expect(game.remaining).toBe(3);
        expect(game.phase).toBe('playing');
        expect(game.act('chord', question.row, question.column, 2400)).toBe(false);
        expect(flag(game, question.mine, 2500)).toBe(false);
        expect(game.remaining).toBe(3);
        for (const cell of question.neighbors) expect(game.board[Math.floor(cell / game.mode.columns)][cell % game.mode.columns]).toBe(cell === question.mine ? 11 : 0);
    });

    it('loses on a single wrong flag and freezes the result', () => {
        const game = new FlagChordTraining(flagChordModes[0], () => 0.37);
        const [question] = game.questions;
        const [safe] = question.neighbors.filter((cell) => cell !== question.mine);
        flag(game, safe, 1000);
        expect(game.act('chord', question.row, question.column, 1500)).toBe(true);
        expect(game.phase).toBe('lost');
        expect(game.remaining).toBe(4);
        expect(game.board[Math.floor(question.mine / game.mode.columns)][question.mine % game.mode.columns]).toBe(15);
        expect(game.board[Math.floor(safe / game.mode.columns)][safe % game.mode.columns]).toBe(14);
        expect(flag(game, safe, 2000)).toBe(false);
        expect(game.elapsedMs(99999)).toBe(500);
    });

    it.each(flagChordModes)('$key finishes after all questions, freezes positive integer milliseconds and keeps games independent', (mode) => {
        for (const duration of [0, 1234.6]) {
            const game = new FlagChordTraining(mode, () => 0.37);
            const fresh = new FlagChordTraining(mode, () => 0.37);
            game.questions.forEach((question, index) => {
                flag(game, question.mine, 8000);
                game.act('chord', question.row, question.column, index === mode.total - 1 ? 8000 + duration : 8000);
                expect(game.remaining).toBe(mode.total - index - 1);
            });
            expect(game.phase).toBe('won');
            expect(game.elapsedMs(99999)).toBe(Math.max(1, Math.round(duration)));
            const [question] = game.questions;
            expect(game.act('chord', question.row, question.column, 99999)).toBe(false);
            expect(fresh.phase).toBe('ready');
            expect(fresh.remaining).toBe(mode.total);
            const copy = fresh.board;
            copy[question.row][question.column] = 99;
            expect(fresh.board[question.row][question.column]).toBe(1);
        }
    });
});
