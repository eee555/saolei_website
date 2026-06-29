import App from './App.vue';
import CardBilibili from './CardBilibili.vue';
import { mockAccountLinksResponse, mockSaoleiImportSummary, mountAccountLink, resetAccountLinkStore } from './testUtils';

import type { AccountLinksResponse } from '@/utils/accountlinks';

describe('<AccountLinksApp />', () => {
    beforeEach(() => {
        resetAccountLinkStore(1, 1);
        mockSaoleiImportSummary();
    });

    it('fetches all details once and renders cards in configured platform order', () => {
        cy.intercept('GET', '**/api/accountlink/1', {
            statusCode: 200,
            body: mockAccountLinksResponse(),
        }).as('fetchAccountLinks');

        mountAccountLink(App, { userId: 1 });

        cy.wait('@fetchAccountLinks');
        cy.contains('Saolei.wang #101');
        cy.contains('Authoritative Minesweeper #202');
        cy.contains('Minesweeper.Online #303');
        cy.contains('Bilibili #404');

        cy.get('.account-link-main > *').then(($cards) => {
            const text = [...$cards].map((card) => card.textContent.replace(/\u00a0/g, ' ')).join('\n');
            expect(text.indexOf('Saolei.wang #101')).to.be.lessThan(text.indexOf('Authoritative Minesweeper #202'));
            expect(text.indexOf('Authoritative Minesweeper #202')).to.be.lessThan(text.indexOf('Minesweeper.Online #303'));
            expect(text.indexOf('Minesweeper.Online #303')).to.be.lessThan(text.indexOf('Bilibili #404'));
        });
    });

    it('handles the add-link event from CardAdd', () => {
        cy.intercept('GET', '**/api/accountlink/1', {
            statusCode: 200,
            body: {
                summary: [],
                B: null,
                c: null,
                a: null,
                w: null,
                q: null,
            } satisfies AccountLinksResponse,
        }).as('fetchAccountLinks');
        cy.intercept('POST', '**/api/accountlink/create/', {
            statusCode: 200,
            body: { id: 5, platform: 'B', identifier: '404', userprofile: 1, verified: false },
        }).as('addLink');

        mountAccountLink(App, { userId: 1 });
        cy.wait('@fetchAccountLinks');

        cy.get('.el-button').first().click();
        cy.get('.el-select').click();
        cy.contains('.el-select-dropdown__item', 'Bilibili').click();
        cy.get('.el-input input').type('404');
        cy.contains('button', 'Confirm').click();

        cy.wait('@addLink').its('request.body').should('equal', 'platform=B&identifier=404');
        cy.get('@fetchAccountLinks.all').should('have.length', 1);
        cy.contains('Bilibili #404');
        cy.contains('This account has not been verified.');
    });

    it('handles refresh emitted by an account card', () => {
        cy.intercept('GET', '**/api/accountlink/1', {
            statusCode: 200,
            body: mockAccountLinksResponse(),
        }).as('fetchAccountLinks');

        mountAccountLink(App, { userId: 1 });
        cy.wait('@fetchAccountLinks');

        cy.get('@vue').then((wrapper: ComponentWrapper<typeof App>) => {
            const card = wrapper.findComponent(CardBilibili) as unknown as { vm: { $emit: (event: 'refresh') => void } };
            card.vm.$emit('refresh');
        });
        cy.wait('@fetchAccountLinks');
    });

    it('does not show the add card when viewing another user', () => {
        resetAccountLinkStore(1, 2);
        cy.intercept('GET', '**/api/accountlink/2', {
            statusCode: 200,
            body: {
                summary: [],
                B: null,
                c: null,
                a: null,
                w: null,
                q: null,
            } satisfies AccountLinksResponse,
        }).as('fetchAccountLinks');

        mountAccountLink(App, { userId: 2 });
        cy.wait('@fetchAccountLinks');

        cy.get('.account-link-main').find('.el-button').should('not.exist');
    });
});
