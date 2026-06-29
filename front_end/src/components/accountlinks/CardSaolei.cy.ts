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

    it('renders the unverified state', () => {
        mountAccountLink(CardSaolei, {
            id: '101',
            verified: false,
        });

        cy.contains('This account has not been verified.');
        cy.contains('Saolei Player').should('not.exist');
    });
});
