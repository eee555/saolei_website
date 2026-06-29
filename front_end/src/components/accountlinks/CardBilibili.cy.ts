import CardBilibili from './CardBilibili.vue';
import { mockBilibiliResponse, mountAccountLink, resetAccountLinkStore } from './testUtils';

import { AccountBilibili } from '@/utils/accountlinks';

describe('<CardBilibili />', () => {
    beforeEach(() => {
        resetAccountLinkStore();
    });

    it('renders bilibili account details without avatar', () => {
        mountAccountLink(CardBilibili, {
            id: '404',
            verified: true,
            info: new AccountBilibili(mockBilibiliResponse()),
        });

        cy.contains('Bilibili #404');
        cy.contains('Bili Player');
        cy.contains('Official Miner');
        cy.contains('Keep mining');
        cy.contains('33');
        cy.get('img').should('not.exist');
    });

    it('renders the unverified state', () => {
        mountAccountLink(CardBilibili, {
            id: '404',
            verified: false,
        });

        cy.contains('This account has not been verified.');
        cy.contains('Bili Player').should('not.exist');
    });
});
