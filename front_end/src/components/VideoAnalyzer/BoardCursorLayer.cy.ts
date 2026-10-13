import type { VueWrapper } from '@vue/test-utils';

import BoardCursorLayer from './BoardCursorLayer.vue';
import type { CursorShape } from './config';

function mountCursor() {
    cy.mount(BoardCursorLayer, { props: { position: { rowIndex: 2.5, columnIndex: 1.5 }, cellSize: 16, shape: 'dot', size: 16 } }).then(({ wrapper }) => {
        cy.wrap(wrapper).as('cursor');
    });
}

describe('<BoardCursorLayer />', () => {
    it('keeps the SVG boundary in absolute pixels, with a small dot and a stable hotspot', () => {
        mountCursor();
        cy.get('.board-cursor-layer').should('have.css', 'left', '24px').and('have.css', 'top', '40px').and('have.css', 'pointer-events', 'none');
        cy.get<SVGSVGElement>('.board-cursor-layer__svg').should(($svg) => {
            expect($svg[0].getBoundingClientRect().width).to.eq(16);
            expect($svg[0].getBoundingClientRect().height).to.eq(16);
            const dot = $svg[0].querySelector<SVGCircleElement>('circle');
            expect((dot?.getBBox().width ?? 0) / 32 * 16).to.eq(3);
        });
        cy.get<VueWrapper>('@cursor').then((wrapper) => wrapper.setProps({ cellSize: 32, size: 40 }));
        cy.get('.board-cursor-layer').should('have.css', 'left', '48px').and('have.css', 'top', '80px');
        cy.get<SVGSVGElement>('.board-cursor-layer__svg').should(($svg) => {
            expect($svg[0].getBoundingClientRect().width).to.eq(40);
            expect($svg[0].getBoundingClientRect().height).to.eq(40);
            const point = $svg[0].createSVGPoint();
            point.x = point.y = 16;
            const matrix = $svg[0].getScreenCTM();
            if (matrix === null) throw new Error('Expected SVG coordinates');
            const center = point.matrixTransform(matrix);
            const root = $svg[0].parentElement?.getBoundingClientRect();
            expect(center.x).to.be.closeTo(root?.left ?? 0, 0.1);
            expect(center.y).to.be.closeTo(root?.top ?? 0, 0.1);
        });
    });

    it('renders each shape, pins the Windows arrow tip and hides missing positions', () => {
        mountCursor();
        for (const shape of ['windows', 'ring', 'crosshair'] as CursorShape[]) {
            cy.get<VueWrapper>('@cursor').then((wrapper) => wrapper.setProps({ shape, size: 4 }));
            cy.get<SVGSVGElement>('.board-cursor-layer__svg').should(($svg) => {
                expect($svg[0].getBoundingClientRect().width).to.eq(4);
                expect($svg[0].querySelectorAll('circle,path').length).to.be.greaterThan(0);
                if (shape === 'windows') {
                    const point = $svg[0].createSVGPoint();
                    point.x = 3;
                    point.y = 2;
                    const matrix = $svg[0].getScreenCTM();
                    if (matrix === null) throw new Error('Expected SVG coordinates');
                    const tip = point.matrixTransform(matrix);
                    const root = $svg[0].parentElement?.getBoundingClientRect();
                    expect(tip.x).to.be.closeTo(root?.left ?? 0, 0.1);
                    expect(tip.y).to.be.closeTo(root?.top ?? 0, 0.1);
                }
            });
        }
        cy.get<VueWrapper>('@cursor').then((wrapper) => wrapper.setProps({ position: null }));
        cy.get('.board-cursor-layer').should('not.be.visible');
        cy.get<VueWrapper>('@cursor').then((wrapper) => wrapper.setProps({ position: { rowIndex: 0, columnIndex: 0 } }));
        cy.get('.board-cursor-layer').should('exist').and('have.css', 'left', '0px').and('have.css', 'top', '0px');
    });
});
