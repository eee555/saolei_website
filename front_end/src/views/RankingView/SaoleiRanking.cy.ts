import SaoleiRanking from './SaoleiRanking.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { pinia } from '@/store/create';

describe('<SaoleiRanking />', () => {
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
        cy.mount(SaoleiRanking, { global: { plugins: [i18n, pinia], config: { globalProperties: { $axios } } } });
        cy.wait('@ranking').its('request.query').should('include', { board: 'saolei', stat: 'sumt', start: '0', end: '20' });
        cy.get('.saolei-ranking-table .el-table__body').extractTableData().should((data) => {
            expect(data[0]).to.include('1.234');
            expect(data[0]?.[0]).to.equal('1');
        });
        cy.get('.el-pagination .btn-next').click();
        cy.wait('@ranking').its('request.query').should('include', { start: '20', end: '40' });
        cy.get('.saolei-ranking-table .el-table__body').extractTableData().should((data) => {
            expect(data[0]?.[0]).to.equal('21');
        });
        cy.get('.saolei-ranking-table th').contains('Beg 3BV/s').click();
        cy.wait('@ranking').its('request.query').should('include', { stat: 'bb', start: '0' });
        cy.get('.el-pagination .btn-next').click();
        cy.wait('@ranking').its('request.query').should('include', { stat: 'bb', start: '20', end: '40' });
        cy.get('.nf-toggle input[type="checkbox"]').check();
        cy.wait('@ranking').its('request.query').should('include', { board: 'saolei_nf', stat: 'bb', start: '0' });
        cy.get('.el-pagination__sizes .el-select').click();
        cy.get('.el-select-dropdown__item').filter(':visible').contains('50').click();
        cy.wait('@ranking').its('request.query').should('include', { board: 'saolei_nf', stat: 'bb', start: '0', end: '50' });
    });
});
