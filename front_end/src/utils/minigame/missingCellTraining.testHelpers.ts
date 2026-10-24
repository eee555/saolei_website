/** 测试用独立判定：逐个假设未开格为唯一安全格，检查所有可见数字。 */
export function missingCellCandidates(board: number[][]): { row: number; column: number }[] {
    const hidden = board.flatMap((row, r) => row.flatMap((value, c) => (value === 10 ? [{ row: r, column: c }] : [])));
    const clues = board.flatMap((row, r) => row.flatMap((value, c) => {
        if (value < 0 || value > 8) return [];
        const covered = hidden.filter((cell) => Math.abs(cell.row - r) <= 1 && Math.abs(cell.column - c) <= 1).length;
        return [{ row: r, column: c, missing: covered - value }];
    }));
    return hidden.filter((cell) => clues.every((clue) => Number(Math.abs(cell.row - clue.row) <= 1 && Math.abs(cell.column - clue.column) <= 1) === clue.missing));
}
