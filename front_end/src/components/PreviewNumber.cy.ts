import PreviewNumber from './PreviewNumber.vue';

import { videoplayerstore } from '@/store';

describe('PreviewNumber', () => {
    beforeEach(() => {
        videoplayerstore.visible = false;
    });

    afterEach(() => {
        videoplayerstore.visible = false;
    });

    it('opens the existing player with the selected video when activated by keyboard', () => {
        cy.intercept('GET', '**/video/get_software/*', { body: { msg: 'e' } }).as('software');
        cy.mount(PreviewNumber, { props: { id: 42, text: '12.345' } });

        cy.contains('button', '12.345').should('have.attr', 'type', 'button').focus();
        cy.realPress('Enter');
        cy.wait('@software').its('request.query.id').should('eq', '42');
        cy.wrap(videoplayerstore).its('visible').should('eq', true);
        cy.wrap(videoplayerstore).its('id').should('eq', 42);
        cy.wrap(videoplayerstore).its('url').should('include', '/api/video/preview?id=42');
        cy.get('@software.all').should('have.length', 1);
    });

    it('renders a non-interactive placeholder without a video', () => {
        cy.mount(PreviewNumber, { props: { id: 0, text: '12.345' } });
        cy.contains('span', '--');
        cy.get('[data-cy=preview-number]').should('not.exist');
    });
});
