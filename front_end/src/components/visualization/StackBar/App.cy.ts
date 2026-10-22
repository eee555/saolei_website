import StackBar from './App.vue';

describe('<StackBar />', () => {
    it('renders segment colors, custom height and widths and updates with data', () => {
        cy.viewport(616, 30);
        cy.mount(StackBar, {
            props: {
                data: [
                    { name: 'A', value: 10, color: '#FF0000' },
                    { name: 'B', value: 20, color: '#00FF00' },
                    { name: 'C', value: 30, color: '#0000FF' },
                ],
                height: '8px',
            },
        });
        cy.get('[data-cy=A]').should('have.css', 'background-color', 'rgb(255, 0, 0)');
        cy.get('[data-cy=A]').should('have.css', 'height', '8px');
        cy.get('[data-cy=B]').should('have.css', 'background-color', 'rgb(0, 255, 0)');
        cy.get('[data-cy=C]').should('have.css', 'background-color', 'rgb(0, 0, 255)');
        cy.get('[data-cy=A]').should('have.css', 'width', '100px');
        cy.get('[data-cy=B]').should('have.css', 'width', '200px');
        cy.get('[data-cy=C]').should('have.css', 'width', '300px');
        cy.get<ComponentWrapper<typeof StackBar>>('@vue').then((wrapper) => wrapper.setProps({
            data: [
                { name: 'A', value: 30, color: '#FF0000' },
                { name: 'B', value: 20, color: '#00FF00' },
                { name: 'C', value: 10, color: '#0000FF' },
            ],
        }));
        cy.get('[data-cy=A]').should('have.css', 'width', '300px');
    });
    it('tooltip', () => {
        cy.viewport(616, 30);
        cy.mount(StackBar, {
            props: {
                data: [
                    { name: 'A', value: 10, color: '#FF0000' },
                    { name: 'B', value: 20, color: '#00FF00' },
                    { name: 'C', value: 30, color: '#0000FF' },
                ],
                formatValue: (value: number) => value.toFixed(2),
            },
        });
        cy.get('[data-cy=A]').trigger('mouseenter');
        cy.get('[id^=tippy-]').should('be.visible').and('contain', 'A: 17%(10.00)');
        cy.get('[data-cy=A]').trigger('mouseleave');
        cy.get('[id^=tippy-]').should('not.exist');
    });
});
