describe('rankings backed by dangerzone fixtures', () => {
    beforeEach(() => {
        cy.flushDatabase();
        cy.clearLocalStorage();
    });

    it('shows speed ranking only after the user binds the video identifier', () => {
        const user = {
            id: 1,
            username: 'speed_ranker',
            realname: 'Speed Ranker',
        };
        const identifier = 'speed-ranking-e2e';

        cy.registerUser(user);
        cy.createIdentifier(identifier);
        cy.createVideo({ user_id: user.id, identifier, level: 'b', timems: 7000, bv: 10 });
        cy.createVideo({ user_id: user.id, identifier, level: 'i', timems: 12000, bv: 30 });
        cy.createVideo({ user_id: user.id, identifier, level: 'e', timems: 30000, bv: 100 });

        cy.intercept('GET', '**/msuser/player_rank/**').as('speedRank');
        cy.visit('/#/ranking/speed');
        cy.wait('@speedRank').its('response.body.players').should('deep.equal', []);
        cy.contains('49.000').should('not.exist');

        cy.bindIdentifier(user.id, identifier, 3);

        cy.reload();
        cy.wait('@speedRank').its('response.body.players').should('have.length', 8);
        cy.contains('Speed Ranker').should('be.visible');
        cy.contains('7.000').should('be.visible');
        cy.contains('12.000').should('be.visible');
        cy.contains('30.000').should('be.visible');
        cy.contains('49.000').should('be.visible');
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
