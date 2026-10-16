describe('Main navigation', () => {
    it('menu navigation', () => {
        cy.visit('/');
        cy.get('#app[data-v-app]', { timeout: Cypress.config('pageLoadTimeout') }).should('be.visible');
        cy.url().should('match', /\/#\/$/);
        cy.get('[data-cy=app-header] [data-navigation-id=ranking] a').click();
        cy.url().should('include', '/#/ranking');
        cy.get('[data-cy=app-header] [data-navigation-id=video] a').click();
        cy.url().should('match', /\/#\/video$/);
        cy.get('[data-cy=app-header] [data-navigation-id=settings] a').click();
        cy.url().should('match', /\/#\/settings$/);
    });
});
