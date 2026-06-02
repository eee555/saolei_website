import type { StaticResponse } from 'cypress/types/net-stubbing';

import PlayerName from './PlayerName.vue';

import $axios from '@/http';
import i18n from '@/i18n';

const recordAbstract = {
    timems: [12345, 45678, 78901],
    timems_id: [101, 102, 103],
    bvs: [1.2345, 2.3456, 3.4567],
    bvs_id: [201, 202, 203],
};
const user = {
    id: 42,
    realname: 'Alice',
    firstname: 'Alicia',
    lastname: 'Mines',
};

function mountPlayerName(userId: number) {
    cy.mount(PlayerName, {
        props: { userId },
        global: {
            plugins: [i18n],
            config: {
                globalProperties: {
                    $axios,
                },
            },
        },
    });
}

function mockUserInfo(response: StaticResponse = { body: user }) {
    cy.intercept('GET', `/api/userprofile/info/${user.id}`, response).as('fetchUser');
}

function mockRecordAbstract() {
    cy.intercept('GET', '/msuser/info_abstract/**', {
        body: { record_abstract: JSON.stringify(recordAbstract) },
    }).as('fetchAbstract');
}

describe('PlayerName', () => {
    beforeEach(() => {
        cy.intercept('GET', '/api/userprofile/avatar/**', {
            statusCode: 404,
        });
    });

    it('shows the fallback name when fetching user info fails', () => {
        cy.on('uncaught:exception', (error) => {
            expect(error.message).to.include('Request failed with status code 500');
            return false;
        });
        mockUserInfo({ statusCode: 500, body: {} });
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
        cy.intercept('GET', '**/api/userprofile/info/**').as('fetchUser');

        mountPlayerName(0);

        cy.contains('Anonymous');
    });

    it('opens the popover and renders abstract records', () => {
        mockUserInfo();
        mockRecordAbstract();

        mountPlayerName(user.id);
        cy.get('[id^=tippy-]').should('not.exist');
        cy.contains(user.realname).realClick();
        cy.wait('@fetchAbstract');

        cy.get('[id^=tippy-]').then((popover) => {
            cy.wrap(popover).contains(user.realname).
                next().contains(`(${user.firstname} ${user.lastname})`).
                next().contains(`#${user.id}`);

            cy.wrap(popover).find('.record-table > div').
                contains('Beg').next().should('contain', '12.345').next().should('contain', '1.234').
                next().contains('Int').next().should('contain', '45.678').next().should('contain', '2.346').
                next().contains('Exp').next().should('contain', '78.901').next().should('contain', '3.457').
                next().contains('Sum').next().should('contain', '136.924').next().should('contain', '7.037');
        });
    });

    it('links to the player page from the popover action', () => {
        mockUserInfo();
        mockRecordAbstract();
        mountPlayerName(user.id);

        cy.contains(user.realname).click();
        cy.contains('[id^=tippy-] a', 'My space').should('have.attr', 'href', `#/player/${user.id}`);
    });
});
