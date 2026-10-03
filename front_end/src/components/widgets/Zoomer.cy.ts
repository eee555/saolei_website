import Zoomer from './Zoomer.vue';

import i18n from '@/i18n';

const mountZoomer = () => cy.mount(Zoomer, { global: { plugins: [i18n] } });

describe('<Zoomer />', () => {
    it('renders', () => {
    // see: https://on.cypress.io/mounting-vue
        mountZoomer();
        cy.get('[data-cy=zoomout]').find('i').should('have.class', 'pi-search-minus');
        cy.get('[data-cy=main]').should('contain', '100%');
        cy.get('[data-cy=zoomin]').find('i').should('have.class', 'pi-search-plus');
    });
    it('zoom button interaction', () => {
        mountZoomer();
        cy.get('[data-cy=zoomout]').click();
        cy.get('[data-cy=main]').should('contain', '90%');
        cy.get('[data-cy=zoomin]').click();
        cy.get('[data-cy=main]').should('contain', '100%');
        cy.get('[data-cy=zoomin]').click();
        cy.get('[data-cy=main]').should('contain', '110%');
    });
    it('scroll interaction', () => {
        mountZoomer();
        cy.get('[data-cy=main]').trigger('wheel', { deltaY: -100 });
        cy.get('[data-cy=main]').should('contain', '110%');
        cy.get('[data-cy=main]').trigger('wheel', { deltaY: 200 });
        cy.get('[data-cy=main]').should('contain', '90%');
    });
    it('min and max', () => {
        mountZoomer();
        cy.get('[data-cy=main]').trigger('wheel', { deltaY: 1000 });
        cy.get('[data-cy=main]').should('contain', '10%');
        cy.get('[data-cy=zoomout]').should('be.disabled').trigger('click', { force: true });
        cy.get('[data-cy=main]').should('contain', '10%');
        cy.get('[data-cy=main]').trigger('wheel', { deltaY: -10000 });
        cy.get('[data-cy=main]').should('contain', '400%');
        cy.get('[data-cy=zoomin]').should('be.disabled').trigger('click', { force: true });
        cy.get('[data-cy=main]').should('contain', '400%');
    });
    it('supports keyboard zoom controls', () => {
        mountZoomer();
        cy.get('[data-cy=zoomin]').should('have.attr', 'aria-label', 'Zoom in').focus();
        cy.realPress('Enter');
        cy.get('[data-cy=main]').should('contain', '110%');
        cy.get('[data-cy=zoomout]').should('have.attr', 'aria-label', 'Zoom out').focus();
        cy.realPress('Space');
        cy.get('[data-cy=main]').should('contain', '100%');
    });
});
