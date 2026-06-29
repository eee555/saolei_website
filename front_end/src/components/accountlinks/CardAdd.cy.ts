import CardAdd from './CardAdd.vue';
import { mockSaoleiResponse, mountAccountLink, resetAccountLinkStore } from './testUtils';

import { AccountLinkPlatform, AccountLinks } from '@/utils/accountlinks';

describe('<CardAdd />', () => {
    beforeEach(() => {
        resetAccountLinkStore();
    });

    it('disables already linked platforms and validates numeric identifiers', () => {
        const accountlinks = new AccountLinks({
            summary: [
                { id: 1, platform: AccountLinkPlatform.Saolei, identifier: '101', userprofile: 1, verified: true },
            ],
            B: null,
            c: mockSaoleiResponse(),
            a: null,
            w: null,
            q: null,
        });

        mountAccountLink(CardAdd, { accountlinks });

        cy.get('.el-button').first().click();
        cy.get('.el-select').click();
        cy.contains('.el-select-dropdown__item', '扫雷网').should('have.class', 'is-disabled');
        cy.contains('.el-select-dropdown__item', 'Bilibili').click();

        cy.contains('button', 'Confirm').should('be.disabled');
        cy.get('.el-input input').type('abc');
        cy.contains('button', 'Confirm').should('be.disabled');
        cy.get('.el-input input').clear();
        cy.get('.el-input input').type('404');
        cy.contains('button', 'Confirm').should('not.be.disabled');
    });

    it('clears the form when the dialog is closed', () => {
        mountAccountLink(CardAdd);

        cy.get('.el-button').first().click();
        cy.get('.el-select').click();
        cy.contains('.el-select-dropdown__item', 'Bilibili').click();
        cy.get('.el-input input').type('404');
        cy.contains('button', 'Cancel').click();
        cy.get('.el-dialog').should('not.be.visible');

        cy.get('.el-button').first().click();
        cy.get('.el-input input').should('have.value', '');
    });
});
