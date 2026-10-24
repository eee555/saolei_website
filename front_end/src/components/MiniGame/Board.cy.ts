import type { BoardBackground, MinesweeperBoard } from '@putianyi888/vue3-minesweeper-board';
import { defineComponent, h } from 'vue';

import Board from './Board.vue';

import { mouseAt } from '@cy/support/minigame';

function mountBoard(board: number[][]) {
    cy.mount(defineComponent({ expose: [], render: () => h(Board, { board, size: 32, label: 'Test board' }) })).then(({ wrapper }) => {
        cy.wrap(wrapper.findComponent(Board)).as('board');
    });
}

describe('shared minigame press preview', () => {
    for (const order of ['left-first', 'right-first']) {
        it(`previews a moving 3x3 region except flags and clears on first release (${order})`, () => {
            const board = Array.from({ length: 5 }, () => [10, 10, 10, 10, 10]);
            board[1][1] = 11;
            board[1][2] = 16;
            board[2][2] = 2;
            mountBoard(board);
            cy.get('.minigame-board-foreground').should('have.css', 'opacity', '1');
            if (order === 'left-first') {
                mouseAt(2, 2, 'mousedown');
                mouseAt(2, 2, 'mousedown', 2, 3);
            } else {
                mouseAt(2, 2, 'mousedown', 2, 2);
                mouseAt(2, 2, 'mousedown', 0, 3);
            }
            cy.get<ComponentWrapper<typeof Board>>('@board').should((wrapper) => {
                const background = wrapper.findComponent<typeof BoardBackground>('.minigame-board-background').props('board');
                expect(background).to.deep.eq([
                    [false, false, false, false, false], [false, false, true, true, false], [false, true, true, true, false], [false, true, true, true, false], [false, false, false, false, false],
                ]);
                expect(wrapper.findComponent<typeof MinesweeperBoard>('.minesweeper-board-content').props('board')).to.deep.eq(board);
            });
            mouseAt(0, 0, 'mousemove', 0, 3);
            cy.get<ComponentWrapper<typeof Board>>('@board').should((wrapper) => {
                const background = wrapper.findComponent<typeof BoardBackground>('.minigame-board-background').props('board');
                expect(background?.[0][0]).to.eq(true);
                expect(background?.[1][1]).to.eq(false);
                expect(background?.[3][3]).to.eq(false);
            });
            mouseAt(0, 0, 'mouseup', 2, 1);
            cy.get<ComponentWrapper<typeof Board>>('@board').should((wrapper) => {
                expect(wrapper.findComponent<typeof BoardBackground>('.minigame-board-background').props('board')).to.eq(undefined);
                expect(wrapper.emitted('action')?.filter(([action]) => action === 'chord')).to.have.length(1);
            });
            mouseAt(0, 0, 'mouseup');
        });
    }

    it('cancels held buttons without generating a chord on blur', () => {
        mountBoard([[10, 16, 11], [10, 2, 10], [10, 10, 10]]);
        mouseAt(1, 1, 'mousedown');
        mouseAt(1, 1, 'mousedown', 2, 3);
        cy.window().trigger('blur');
        mouseAt(1, 1, 'mouseup', 0, 2);
        mouseAt(1, 1, 'mouseup', 2, 0);
        cy.get<ComponentWrapper<typeof Board>>('@board').should((wrapper) => {
            expect(wrapper.emitted('action')).to.eq(undefined);
            expect(wrapper.findComponent<typeof BoardBackground>('.minigame-board-background').props('board')).to.eq(undefined);
        });
    });
});
