import StackBar from './App.vue';

describe('<StackBar />', () => {
    it('renders', () => {
    // see: https://on.cypress.io/mounting-vue
        cy.mount(StackBar, {
            props: {
                data: [
                    { name: 'A', value: 10, color: '#FF0000' },
                    { name: 'B', value: 20, color: '#00FF00' },
                    { name: 'C', value: 30, color: '#0000FF' },
                ],
                style: 'width: 600px;',
            },
        });
        cy.get('[data-cy=A]').should('have.css', 'background-color', 'rgb(255, 0, 0)');
        cy.get('[data-cy=B]').should('have.css', 'background-color', 'rgb(0, 255, 0)');
        cy.get('[data-cy=C]').should('have.css', 'background-color', 'rgb(0, 0, 255)');
        cy.get('[data-cy=A]').should('have.css', 'width', '100px');
        cy.get('[data-cy=B]').should('have.css', 'width', '200px');
        cy.get('[data-cy=C]').should('have.css', 'width', '300px');
    });
    it('tooltip', () => {
        cy.mount(StackBar, {
            props: {
                data: [
                    { name: 'A', value: 10, color: '#FF0000' },
                    { name: 'B', value: 20, color: '#00FF00' },
                    { name: 'C', value: 30, color: '#0000FF' },
                ],
                style: 'width: 600px;',
            },
        });
        cy.get('[data-cy=A]').trigger('mouseenter');
        cy.get('[id^=tippy-]').should('be.visible').and('contain', 'A: 17%(10)');
        cy.get('[data-cy=A]').trigger('mouseleave');
        cy.get('[id^=tippy-]').should('not.exist');
        cy.get('[data-cy=B]').trigger('mouseenter');
        cy.get('[id^=tippy-]').should('be.visible').and('contain', 'B: 33%(20)');
        cy.get('[data-cy=B]').trigger('mouseleave');
        cy.get('[id^=tippy-]').should('not.exist');
        cy.get('[data-cy=C]').trigger('mouseenter');
        cy.get('[id^=tippy-]').should('be.visible').and('contain', 'C: 50%(30)');
        cy.get('[data-cy=C]').trigger('mouseleave');
    });
    it('reactive to data', () => {
        const data = [
            { name: 'A', value: 10, color: '#FF0000' },
            { name: 'B', value: 20, color: '#00FF00' },
            { name: 'C', value: 30, color: '#0000FF' },
        ];
        cy.mount(StackBar, {
            propsData: {
                data: data,
                style: 'width: 600px;',
            },
        });
        cy.get('@vue').then((wrapper) => {
            wrapper.setProps({
                data: [
                    { name: 'A', value: 30, color: '#FF0000' },
                    { name: 'B', value: 20, color: '#00FF00' },
                    { name: 'C', value: 10, color: '#0000FF' },
                ],
            });
        });
        cy.get('[data-cy=A]').should('have.css', 'width', '300px');
    });
});
