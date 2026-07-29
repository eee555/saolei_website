import App from './App.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { store } from '@/store';
import { pinia } from '@/store/create';
import { UserProfile } from '@/utils/userprofile';

type RecordMode = 'dg' | 'nf' | 'ng' | 'std';

function recordFields(mode: RecordMode, seed: number) {
    return {
        [`b_timems_${mode}`]: 10000 + seed,
        [`i_timems_${mode}`]: 20000 + seed,
        [`e_timems_${mode}`]: 30000 + seed,
        [`b_bvs_${mode}`]: 1.1 + seed,
        [`i_bvs_${mode}`]: 2.2 + seed,
        [`e_bvs_${mode}`]: 3.3 + seed,
        [`b_stnb_${mode}`]: 11.1 + seed,
        [`i_stnb_${mode}`]: 22.2 + seed,
        [`e_stnb_${mode}`]: 33.3 + seed,
        [`b_ioe_${mode}`]: 4.4 + seed,
        [`i_ioe_${mode}`]: 5.5 + seed,
        [`e_ioe_${mode}`]: 6.6 + seed,
        [`b_path_${mode}`]: 7.7 + seed,
        [`i_path_${mode}`]: 8.8 + seed,
        [`e_path_${mode}`]: 9.9 + seed,
        [`b_timems_id_${mode}`]: 101 + seed,
        [`i_timems_id_${mode}`]: 102 + seed,
        [`e_timems_id_${mode}`]: 103 + seed,
        [`b_bvs_id_${mode}`]: 201 + seed,
        [`i_bvs_id_${mode}`]: 202 + seed,
        [`e_bvs_id_${mode}`]: 203 + seed,
        [`b_stnb_id_${mode}`]: 301 + seed,
        [`i_stnb_id_${mode}`]: 302 + seed,
        [`e_stnb_id_${mode}`]: 303 + seed,
        [`b_ioe_id_${mode}`]: 401 + seed,
        [`i_ioe_id_${mode}`]: 402 + seed,
        [`e_ioe_id_${mode}`]: 403 + seed,
        [`b_path_id_${mode}`]: 501 + seed,
        [`i_path_id_${mode}`]: 502 + seed,
        [`e_path_id_${mode}`]: 503 + seed,
    };
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

        cy.intercept({ method: 'GET', pathname: '/api/msuser/records' }, {
            body: {
                ...recordFields('std', 0),
                ...recordFields('nf', 10),
                ...recordFields('ng', 20),
                ...recordFields('dg', 30),
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

        cy.wait('@classicRecords').its('request.query').should('deep.equal', { user_id: '42' });
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
