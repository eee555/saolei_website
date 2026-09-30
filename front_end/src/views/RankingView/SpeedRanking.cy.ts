import PrimeVue from 'primevue/config';

import SpeedRanking from './SpeedRanking.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { pinia } from '@/store/create';

describe('<SpeedRanking />', () => {
    it('loads pages, switches stats and independently selects NF', () => {
        cy.mockPlayerNameFallback();
        cy.intercept({ method: 'GET', pathname: '/api/speedranking/rank' }, {
            body: { count: 21,
                players: [{
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
                }] },
        }).as('ranking');
        cy.mount(SpeedRanking, { global: { plugins: [i18n, pinia, PrimeVue], config: { globalProperties: { $axios } } } });
        cy.wait('@ranking').its('request.query').should('include', { board: 'saolei', stat: 'sumt', start: '0', end: '20' });
        cy.get('.speed-ranking').contains('1.234').should('be.visible');
        cy.get('.p-paginator-next').click();
        cy.wait('@ranking').its('request.query').should('include', { start: '20', end: '40' });
        cy.get('.speed-ranking th').contains('Beg 3BV/s').click();
        cy.wait('@ranking').its('request.query').should('include', { stat: 'bb', start: '0' });
        cy.get('.speed-ranking input[type="checkbox"]').check();
        cy.wait('@ranking').its('request.query').should('include', { board: 'saolei_nf', stat: 'bb', start: '0' });
    });
});
