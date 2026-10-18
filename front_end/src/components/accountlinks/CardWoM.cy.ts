import CardWoM from './CardWoM.vue';
import { mockUpdateAccountLink, mockWoMResponse, mountAccountLink, resetAccountLinkStore } from './testUtils';

import { AccountWoM } from '@/utils/accountlinks';

describe('<CardWoM />', () => {
    beforeEach(() => {
        resetAccountLinkStore();
    });

    it('renders account details, public records and lifetime statistics', () => {
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

        cy.get('.el-link').last().click();
        cy.contains('.el-carousel__item.is-active', 'Games').should('contain', '111645');
        cy.get('.el-link').last().click();
        cy.contains('.el-carousel__item.is-active', 'NG Time (B/I/E)').should('contain', '1.282 | 16.720 | 48.877');
        cy.contains('.el-carousel__item.is-active', 'Endurance Time (B/I/E)').should('contain', '00:09:42 | 00:43:11 | 03:51:28');
        cy.contains('.el-carousel__item.is-active', 'NF Wins').should('contain', '16207');
        cy.get('.el-link').last().click();
        cy.contains('.el-carousel__item.is-active', 'Lifetime Minecoins Earned').should('contain', '2000');
        cy.contains('.el-carousel__item.is-active', 'Lifetime Arena Coins Earned').should('contain', '0');
        cy.contains('.el-carousel__item.is-active', 'Total Play Time').should('contain', '02:00:00');
        cy.get('img[src*="/img/gems"], img[src*="/img/eq.svg"]').should('not.exist');
    });

    it('shows the default endurance time and placeholders for missing no-guess records', () => {
        mountAccountLink(CardWoM, {
            id: '303',
            verified: true,
            info: new AccountWoM(mockWoMResponse({ b_ng_t_ms: null, i_ng_t_ms: null, e_ng_t_ms: null, b_endurance_ms: 86400000, i_endurance_ms: 86400000, e_endurance_ms: 86400000 })),
        });

        cy.get('.el-link').last().click();
        cy.contains('.el-carousel__item.is-active', 'Games').should('be.visible');
        cy.get('.el-link').last().click();
        cy.contains('.el-carousel__item.is-active', 'NG Time (B/I/E)').should('contain', '- | - | -');
        cy.contains('.el-carousel__item.is-active', 'Endurance Time (B/I/E)').should('contain', '24:00:00 | 24:00:00 | 24:00:00');
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
        cy.get('.el-link').last().click();
        cy.get('.el-link').last().click();
        cy.contains('button', 'Synchronize').click();

        cy.wait('@updateAccountLink').its('request.body').should('equal', 'platform=w');
        cy.contains('Update failed: The third-party page structure changed, so data extraction failed');
    });
});
