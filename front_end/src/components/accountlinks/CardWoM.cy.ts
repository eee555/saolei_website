import CardWoM from './CardWoM.vue';
import { mockUpdateAccountLink, mockWoMResponse, mountAccountLink, resetAccountLinkStore } from './testUtils';

import { AccountWoM } from '@/utils/accountlinks';

describe('<CardWoM />', () => {
    beforeEach(() => {
        resetAccountLinkStore();
    });

    it('renders Minesweeper.Online account details', () => {
        mountAccountLink(CardWoM, {
            id: '303',
            verified: true,
            info: new AccountWoM(mockWoMResponse()),
        });

        cy.contains('Minesweeper.Online #303');
        cy.contains('123');
        cy.contains('12.000 | 45.000 | 99.000');
        cy.contains('1.23 | 2.34 | 3.45');
        cy.contains('88 | 77 | 66');
    });

    it('renders the unverified state', () => {
        mountAccountLink(CardWoM, {
            id: '303',
            verified: false,
        });

        cy.contains('This account has not been verified.');
        cy.contains('123').should('not.exist');
    });

    it('shows a readable parse error when synchronization returns indexerror', () => {
        mockUpdateAccountLink({
            type: 'error',
            object: 'import',
            category: 'indexerror',
        });

        mountAccountLink(CardWoM, {
            id: '303',
            verified: true,
            info: new AccountWoM(mockWoMResponse()),
        });

        cy.get('.el-link').last().click();
        cy.get('.el-link').last().click();
        cy.contains('button', 'Synchronize').click();

        cy.wait('@updateAccountLink').its('request.body').should('equal', 'platform=w');
        cy.contains('Update failed: The third-party page structure changed, so data extraction failed');
    });
});
