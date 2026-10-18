import type { StaticResponse } from 'cypress/types/net-stubbing';
import { h } from 'vue';
import { createRouter, createWebHashHistory } from 'vue-router';

import PlayerName from './PlayerName.vue';

import $axios from '@/http';
import i18n from '@/i18n';

const user = {
    id: 42,
    realname: 'Alice',
    firstname: 'Alicia',
    lastname: 'Mines',
};

function hashRouter() {
    const router = createRouter({
        history: createWebHashHistory(),
        routes: [{ path: '/:pathMatch(.*)*', component: { render: () => h('div') } }],
    });
    void router.push('/');
    return router;
}

function mountPlayerName(userId: number, options: { interactive?: boolean; onParentClick?: () => void } = {}) {
    const router = hashRouter();
    cy.wrap(router.isReady()).then(() => {
        cy.mount({
            render: () => h('div', { onClick: options.onParentClick }, [
                h(PlayerName, { userId, interactive: options.interactive }),
            ]),
        }, {
            global: {
                plugins: [i18n, router],
                config: { globalProperties: { $axios } },
            },
        });
    });
}

function mockUserInfo(response: StaticResponse = { body: [user] }) {
    cy.intercept('GET', `/api/userprofile/infobulk?ids=${user.id}`, response).as('fetchUser');
}

describe('PlayerName', () => {
    let previousUrl: string;

    beforeEach(() => {
        cy.window().then((window) => {
            previousUrl = window.location.href;
        });
        cy.intercept('GET', '/api/userprofile/avatar/**', {
            statusCode: 404,
        });
        // cy.intercept('GET', '/api/userprofile/infoupdated?**', {
        //     body: [user.id],
        // }).as('getInfoUpdated');
    });

    afterEach(() => {
        cy.window().then((window) => {
            window.history.replaceState(null, '', previousUrl);
        });
    });

    it('shows the fallback name when server error', () => {
        cy.on('uncaught:exception', (error) => {
            expect(error.message).to.include('Request failed with status code 500');
            return false;
        });
        mockUserInfo({ statusCode: 500, body: {} });
        mountPlayerName(user.id);

        cy.wait('@fetchUser');
        cy.contains(`User#${user.id}`);
    });

    it('shows the fallback name when no user info', () => {
        mockUserInfo({ body: [] });
        mountPlayerName(user.id);

        cy.wait('@fetchUser');
        cy.contains(`User#${user.id}`);
    });

    it('renders the fetched user name when loading succeeds', () => {
        mockUserInfo();
        mountPlayerName(user.id);

        cy.contains(user.realname);
    });

    it('does not fetch user info when userId is zero', () => {
        cy.intercept('GET', '**/api/userprofile/infobulk?**').as('fetchUser');

        mountPlayerName(0);

        cy.contains('Anonymous');
    });

    it('links directly to the player page', () => {
        mockUserInfo();
        mountPlayerName(user.id);

        cy.contains('a', user.realname).should('have.attr', 'href', `#/player/${user.id}`);
    });

    it('lets clicks bubble without opening a popover when not interactive', () => {
        cy.mockPlayerNameFallback();
        const onParentClick = cy.stub().as('parentClick');
        mountPlayerName(101, { interactive: false,
            onParentClick: () => {
                onParentClick();
            } });

        cy.contains('User#101').click();

        cy.get('@parentClick').should('have.been.calledOnce');
        cy.get('[id^=tippy-]').should('not.exist');
        cy.get('[data-cy-root] a').should('not.exist');
    });
});
