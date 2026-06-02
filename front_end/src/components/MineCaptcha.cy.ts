import MineCaptcha from './MineCaptcha.vue';

import $axios from '@/http';
import i18n from '@/i18n';

const mountOptions = {
    global: {
        plugins: [i18n],
        config: {
            globalProperties: {
                $axios,
            },
        },
    },
};

describe('<MineCaptcha />', () => {
    beforeEach(() => {
        cy.intercept('GET', '/userprofile/refresh_captcha/', {
            statusCode: 200,
            body: { status: 100, hashkey: 'test-key', top: [1, 2, 1, 2, 1] },
        }).as('refresh');
    });

    it('renders 5 number cells and 5 clickable cells', () => {
        cy.mount(MineCaptcha, mountOptions);
        cy.wait('@refresh');
        // top numbers: 5 .revealed; bottom: 5 .unrevealed initially
        cy.get('.cell.revealed').should('have.length', 5);
        cy.get('.cell.unrevealed').should('have.length', 5);
    });

    it('toggles opened state on bottom-cell click', () => {
        cy.mount(MineCaptcha, mountOptions);
        cy.wait('@refresh');
        cy.get('[data-cy=mine-cell-0]').click();
        cy.get('[data-cy=mine-cell-0]').should('have.class', 'opened');
        cy.get('[data-cy=mine-cell-0]').click();
        cy.get('[data-cy=mine-cell-0]').should('not.have.class', 'opened');
    });

    it('top number cells do not toggle', () => {
        cy.mount(MineCaptcha, mountOptions);
        cy.wait('@refresh');
        // First .revealed is a top-row number cell, not a bottom cell.
        cy.get('.cell.revealed').first().click({ force: true });
        cy.get('.cell.revealed').first().should('not.have.class', 'opened');
    });

    it('getResponse() returns sorted comma-separated indices', () => {
        cy.mount(MineCaptcha, mountOptions).then(({ wrapper }) => {
            cy.wait('@refresh').then(() => {
                cy.get('[data-cy=mine-cell-3]').click();
                cy.get('[data-cy=mine-cell-1]').click();
                cy.wrap(null).then(() => {
                    // @ts-expect-error vm typing
                    expect(wrapper.vm.getResponse()).to.equal('1,3');
                });
            });
        });
    });
});
