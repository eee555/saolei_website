describe('rankings backed by dangerzone fixtures', () => {
    beforeEach(() => {
        cy.flushDatabase();
        cy.clearLocalStorage();
    });

    it('shows pluck ranking only after the user binds the video identifier', () => {
        const user = {
            id: 1,
            username: 'pluck_ranker',
            realname: 'Pluck Ranker',
        };
        const identifier = 'pluck-ranking-e2e';

        cy.registerUser(user);
        cy.createIdentifier(identifier);
        cy.createVideo({
            user_id: user.id,
            identifier,
            level: 'c8_8_40',
            timems: 10000,
            bv: 40,
            pluck: 0.123456,
        });

        cy.intercept('GET', '**/api/customranking/pluck?**').as('pluckRank');
        cy.visit('/#/ranking/density');
        cy.wait('@pluckRank').its('response.body').should('deep.include', {
            count: 0,
        });
        cy.contains('0.123456').should('not.exist');

        cy.bindIdentifier(user.id, identifier, 1);

        cy.reload();
        cy.wait('@pluckRank').its('response.body.count').should('eq', 1);
        cy.contains('Pluck Ranker').should('be.visible');
        cy.contains('0.123456').should('be.visible');
        cy.contains('10.000').should('be.visible');
        cy.contains('40').should('be.visible');
    });
});
