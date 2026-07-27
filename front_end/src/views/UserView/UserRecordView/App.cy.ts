import App from './App.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { store } from '@/store';
import { pinia } from '@/store/create';
import { UserProfile } from '@/utils/userprofile';

function recordBIE(seed: number) {
    return JSON.stringify({
        timems: [10000 + seed, 20000 + seed, 30000 + seed],
        bvs: [1.1 + seed, 2.2 + seed, 3.3 + seed],
        stnb: [11.1 + seed, 22.2 + seed, 33.3 + seed],
        ioe: [4.4 + seed, 5.5 + seed, 6.6 + seed],
        path: [7.7 + seed, 8.8 + seed, 9.9 + seed],
        timems_id: [101 + seed, 102 + seed, 103 + seed],
        bvs_id: [201 + seed, 202 + seed, 203 + seed],
        stnb_id: [301 + seed, 302 + seed, 303 + seed],
        ioe_id: [401 + seed, 402 + seed, 403 + seed],
        path_id: [501 + seed, 502 + seed, 503 + seed],
    });
}

const mountOptions = {
    global: {
        plugins: [i18n, pinia],
        config: {
            globalProperties: {
                $axios,
            },
        },
    },
};

describe('<UserRecordViewApp />', () => {
    beforeEach(() => {
        store.$reset();
        store.player = new UserProfile({ id: 42, realname: 'Test Player' });

        cy.intercept({ method: 'GET', pathname: '/msuser/records/' }, {
            body: {
                status: 100,
                id: 42,
                realname: 'Test Player',
                std_record: recordBIE(0),
                nf_record: recordBIE(10),
                ng_record: recordBIE(20),
                dg_record: recordBIE(30),
            },
        }).as('classicRecords');

        cy.intercept({ method: 'GET', pathname: '/api/customranking/pluck/player' }, {
            body: [
                {
                    level: 'c8_8_40',
                    video_id: 9001,
                    pluck: 0.123456,
                },
                {
                    level: 'c16_30_150',
                    video_id: 9002,
                    pluck: 0.987654,
                },
            ],
        }).as('pluckRecords');
    });

    it('loads and renders classical records plus a complete pluck record table', () => {
        cy.mount(App, mountOptions);

        cy.wait('@classicRecords').its('request.query').should('deep.equal', { id: '42' });
        cy.wait('@pluckRecords').its('request.query').should('deep.equal', { player_id: '42' });

        cy.contains('Standard').should('be.visible');
        cy.contains('No Flag').should('be.visible');
        cy.contains('No Guessing').should('be.visible');
        cy.contains('Recursive Chord').should('be.visible');
        cy.contains('.clickable', '10.000').should('be.visible');
        cy.contains('.clickable', '1.100').should('be.visible');

        cy.get('.pluck-record-table tbody tr').should('have.length', 4);
        cy.get('.pluck-record-table').within(() => {
            cy.contains('8x8/40').should('be.visible');
            cy.contains('16x16/100').should('be.visible');
            cy.contains('16x30/150').should('be.visible');
            cy.contains('24x30/200').should('be.visible');
            cy.contains('.clickable', '0.123456').should('be.visible');
            cy.contains('.clickable', '0.987654').should('be.visible');
        });
        cy.get('.pluck-record-table tbody tr').eq(1).contains('--').should('be.visible');
        cy.get('.pluck-record-table tbody tr').eq(3).contains('--').should('be.visible');
    });
});
