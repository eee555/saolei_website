import type { StaticResponse } from 'cypress/types/net-stubbing';

import PlayerName from './PlayerName.vue';

import $axios from '@/http';
import i18n from '@/i18n';

const recordAbstract = {
    b_timems_std: 12345,
    i_timems_std: 45678,
    e_timems_std: 78901,
    b_timems_id_std: 101,
    i_timems_id_std: 102,
    e_timems_id_std: 103,
    b_bvs_std: 1.2345,
    i_bvs_std: 2.3456,
    e_bvs_std: 3.4567,
    b_bvs_id_std: 201,
    i_bvs_id_std: 202,
    e_bvs_id_std: 203,
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

function mockUserInfo(response: StaticResponse = { body: [user] }) {
    cy.intercept('GET', `/api/userprofile/infobulk?ids=${user.id}`, response).as('fetchUser');
}

function mockRecordAbstract() {
    cy.intercept({ method: 'GET', pathname: '/api/msuser/records_abstract' }, {
        body: recordAbstract,
    }).as('fetchAbstract');
}

describe('PlayerName', () => {
    beforeEach(() => {
        cy.intercept('GET', '/api/userprofile/avatar/**', {
            statusCode: 404,
        });
        // cy.intercept('GET', '/api/userprofile/infoupdated?**', {
        //     body: [user.id],
        // }).as('getInfoUpdated');
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
