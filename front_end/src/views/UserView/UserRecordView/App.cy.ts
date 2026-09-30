import App from './App.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { store } from '@/store';
import { pinia } from '@/store/create';
import { UserProfile } from '@/utils/userprofile';

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
        cy.intercept({ method: 'GET', pathname: '/api/speedranking/player/42' }, {
            body: {
                player_id: 42,
                bt: 1234,
                bb: 4.567,
                it: null,
                ib: null,
                et: null,
                eb: null,
                sumt: 2001232,
                sumb: 4.567,
                bt_id: 8001,
                bb_id: 8002,
                it_id: null,
                ib_id: null,
                et_id: null,
                eb_id: null,
            },
        }).as('saoleiRecords');

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

    it('loads and renders a complete pluck record table', () => {
        cy.mount(App, mountOptions);

        cy.wait('@pluckRecords').its('request.query').should('deep.equal', { player_id: '42' });

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
        cy.get('.saolei-record-table tbody tr').should('have.length', 2);
        cy.get('.saolei-record-table').within(() => {
            cy.contains('1.234').should('be.visible');
            cy.contains('4.567').should('be.visible');
            cy.contains('--').should('be.visible');
        });
    });
});
