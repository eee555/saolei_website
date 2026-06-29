import CardMsgames from './CardMsgames.vue';
import { mockMSGamesResponse, mountAccountLink } from './testUtils';

import { AccountMSGames } from '@/utils/accountlinks';

describe('<CardMsgames />', () => {
    it('renders Authoritative Minesweeper account details', () => {
        mountAccountLink(CardMsgames, {
            id: '202',
            verified: true,
            info: new AccountMSGames(mockMSGamesResponse()),
        });

        cy.contains('Authoritative Minesweeper #202');
        cy.contains('AM Player');
        cy.contains('Local AM');
        cy.contains('2024-01-01 01:00:00');
    });

    it('renders the unverified state', () => {
        mountAccountLink(CardMsgames, {
            id: '202',
            verified: false,
        });

        cy.contains('This account has not been verified.');
        cy.contains('AM Player').should('not.exist');
    });
});
