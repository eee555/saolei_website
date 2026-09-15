import CardAddMineracer from './CardAddMineracer.vue';
import { mockMineracerAccountLinkSessionResponse, mountAccountLink, resetAccountLinkStore } from './testUtils';

describe('<CardAddMineracer />', () => {
    beforeEach(() => {
        resetAccountLinkStore();
        cy.clock(new Date('2025-05-09T12:13:14Z'));
    });

    it('starts a Mineracer link session and polls when next_poll_at is reached', () => {
        cy.intercept('POST', '**/api/accountlink/mineracer/start/', {
            statusCode: 200,
            body: mockMineracerAccountLinkSessionResponse({
                expires_at: '2025-05-09T12:23:14Z',
                next_poll_at: '2025-05-09T12:13:16Z',
            }),
        }).as('startMineracerLink');
        cy.intercept('GET', '**/api/accountlink/mineracer/status/mineracer-session-1', {
            statusCode: 200,
            body: mockMineracerAccountLinkSessionResponse({
                status: 'confirmed',
                expires_at: '2025-05-09T12:23:14Z',
                next_poll_at: null,
                remote_userid: '123456789',
            }),
        }).as('fetchMineracerLinkStatus');
        const onRefresh = cy.stub().as('refresh');

        mountAccountLink(CardAddMineracer, { onRefresh });
        cy.contains('button', 'Generate link').click();

        cy.wait('@startMineracerLink');
        cy.contains('Waiting for Mineracer');
        cy.get('a[href="https://mineracer.com/link?code=ABCD-EFGH"]').should('have.attr', 'target', '_blank');
        cy.get('@fetchMineracerLinkStatus.all').should('have.length', 0);

        cy.tick(2000);
        cy.wait('@fetchMineracerLinkStatus');

        cy.contains('Mineracer account linked.');
        cy.contains('123456789');
        cy.get('@refresh').should('have.been.calledOnce');
    });

    it('shows mapped Mineracer errors returned by the start API', () => {
        cy.intercept('POST', '**/api/accountlink/mineracer/start/', {
            statusCode: 409,
            body: { type: 'error', object: 'mineracer', category: 'identifier_conflict' },
        }).as('startMineracerLink');

        mountAccountLink(CardAddMineracer);
        cy.contains('button', 'Generate link').click();

        cy.wait('@startMineracerLink');
        cy.contains('This Mineracer account is already linked to another user.');
    });
});
