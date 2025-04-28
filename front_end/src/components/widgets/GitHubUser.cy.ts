import GitHubUser from './GitHubUser.vue';

describe('<GitHubUser />', () => {
    it('renders', () => {
        // see: https://on.cypress.io/mounting-vue
        cy.mount(GitHubUser, {
            props: {
                username: 'putianyi889',
            },
        });
        cy.get('span').should('contain', 'putianyi889');
        cy.get('img').should('have.attr', 'src').and('contain', 'https://avatars.githubusercontent.com/putianyi889');
    });
});
