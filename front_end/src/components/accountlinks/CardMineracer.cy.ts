import CardMineracer from './CardMineracer.vue';
import { mockMineracerResponse, mountAccountLink } from './testUtils';

import { AccountMineracer } from '@/utils/accountlinks';

describe('<CardMineracer />', () => {
    it('renders Mineracer account details', () => {
        mountAccountLink(CardMineracer, {
            id: '123456789',
            verified: true,
            info: new AccountMineracer(mockMineracerResponse()),
        });

        cy.contains('Mineracer #123456789');
        cy.contains('Mineracer User ID');
        cy.contains('Verified');
        cy.contains('2025-05-09 20:13:14');
        cy.get('a[href="https://mineracer.com/"]').should('have.attr', 'target', '_blank');
        cy.get('a[href="https://mineracer.com/"]').should('have.attr', 'rel', 'noopener noreferrer');
    });

    it('renders the unverified state', () => {
        mountAccountLink(CardMineracer, {
            id: '123456789',
            verified: false,
        });

        cy.contains('This account has not been verified.');
        cy.contains('Mineracer User ID').should('not.exist');
    });
});
