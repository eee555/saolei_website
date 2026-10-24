import CardSaolei from './CardSaolei.vue';
import { mockSaoleiImportSummary, mockSaoleiResponse, mountAccountLink, resetAccountLinkStore } from './testUtils';

import { AccountSaolei } from '@/utils/accountlinks';

describe('<CardSaolei />', () => {
    beforeEach(() => {
        resetAccountLinkStore();
        mockSaoleiImportSummary();
    });

    it('renders saolei account details and import summary', () => {
        mountAccountLink(CardSaolei, {
            id: '101',
            verified: true,
            info: new AccountSaolei(mockSaoleiResponse()),
        });

        cy.contains('Saolei.wang #101');
        cy.contains('Saolei Player');
        cy.contains('9876');
        cy.contains('12.34');
        cy.wait('@importSummary');
        cy.contains('已收藏3个录像');
    });

    it('keeps the synchronization layout disabled and allows viewing saved imports', () => {
        cy.clock(Date.now(), ['setInterval', 'clearInterval']);
        cy.intercept('POST', '**/accountlink/saolei_import*', () => {
            throw new Error('Replay crawling must remain disabled');
        });
        cy.intercept('POST', '**/accountlink/update/', () => {
            throw new Error('Profile crawling must remain disabled');
        });
        cy.intercept('GET', '**/accountlink/saolei/videolist/get/*', { body: [] }).as('savedVideos');
        mountAccountLink(CardSaolei, {
            id: '101', verified: true, info: new AccountSaolei(mockSaoleiResponse()),
        });
        cy.wait('@importSummary');

        cy.get('.p-toolbar .el-link').eq(1).click();
        cy.contains('Profile refresh and replay synchronization are disabled');
        cy.contains('button', 'Synchronize').should('be.disabled');
        cy.contains('button', '更新').should('be.disabled');
        cy.contains('button', 'Manage').click();
        cy.wait('@savedVideos');
        cy.tick(60000);
        cy.get('@importSummary.all').should('have.length', 1);
    });

    it('renders the unverified state', () => {
        mountAccountLink(CardSaolei, {
            id: '101',
            verified: false,
        });

        cy.contains('This account has not been verified.');
        cy.contains('Saolei Player').should('not.exist');
    });
});
