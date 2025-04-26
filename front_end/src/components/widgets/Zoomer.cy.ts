import Zoomer from './Zoomer.vue';

describe('<Zoomer />', () => {
    it('renders', () => {
    // see: https://on.cypress.io/mounting-vue
        cy.mount(Zoomer);
        cy.get('[data-cy=zoomout]').get('i').should('have.class', 'pi-search-minus');
        cy.get('[data-cy=main').should('contain', '100%');
        cy.get('[data-cy=zoomin]').get('i').should('have.class', 'pi-search-plus');
    });
    it('zoom button interaction', () => {
        cy.mount(Zoomer);
        cy.get('[data-cy=zoomout]').click();
        cy.get('[data-cy=main').should('contain', '90%');
        cy.get('[data-cy=zoomin]').click();
        cy.get('[data-cy=main').should('contain', '100%');
        cy.get('[data-cy=zoomin]').click();
        cy.get('[data-cy=main').should('contain', '110%');
    });
    it('scroll interaction', () => {
        cy.mount(Zoomer);
        cy.get('[data-cy=main]').trigger('wheel', { deltaY: -100 });
        cy.get('[data-cy=main').should('contain', '110%');
        cy.get('[data-cy=main]').trigger('wheel', { deltaY: 100 });
        cy.get('[data-cy=main').should('contain', '100%');
        cy.get('[data-cy=main]').trigger('wheel', { deltaY: 100 });
        cy.get('[data-cy=main').should('contain', '90%');
    });
});
