import { defineComponent, h } from 'vue';

import BaseOverlay from './BaseOverlay.vue';

import i18n from '@/i18n';

describe('BaseOverlay trigger', () => {
    it('opens by keyboard without triggering the parent action and keeps its slots', () => {
        const parentClick = cy.spy().as('parentClick');
        cy.mount(defineComponent({
            expose: [],
            render: () => h('div', { onClick: parentClick }, [
                h(BaseOverlay, { underline: 'always' }, {
                    default: () => 'Open details',
                    header: () => 'Details',
                    overlay: () => 'Detail content',
                }),
            ]),
        }), { global: { plugins: [i18n] } });

        cy.get('.el-dialog').should('not.exist');
        cy.contains('button', 'Open details').should('have.css', 'text-decoration-line', 'underline').focus();
        cy.realPress('Enter');
        cy.get('@parentClick').should('not.have.been.called');
        cy.get('.el-dialog').should('be.visible').and('contain', 'Details').and('contain', 'Detail content');
        cy.get('body').click(0, 0);
        cy.shouldBeAbsentOrHidden('.el-dialog');
    });
});
