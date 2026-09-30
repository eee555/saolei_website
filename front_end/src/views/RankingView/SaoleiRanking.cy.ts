import SaoleiRanking from './SaoleiRanking.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { pinia } from '@/store/create';

describe('<SaoleiRanking />', () => {
    it('renders grouped columns, loads pages, switches stats and independently selects NF', () => {
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
        cy.get('.saolei-ranking-table .el-table__header').extractTableData().should((data) => {
            expect(data[0]).to.deep.equal(['', 'Player', 'Beginner', 'Intermediate', 'Expert', 'Sum']);
            expect(data[1]).to.deep.equal(['Time', 'Bvs', 'Time', 'Bvs', 'Time', 'Bvs', 'Time', 'Bvs']);
        });
        cy.get('.saolei-ranking-table .el-table__body').extractTableData().should((data) => {
            expect(data[0]?.slice(2)).to.deep.equal(['1.234', '4.567', '--', '--', '--', '--', '2001.232', '4.567']);
            expect(data[0]?.[0]).to.equal('1');
        });
        cy.get('.stat-header[aria-label="Sum Time"]').should('have.attr', 'aria-pressed', 'true');
        cy.get('.saolei-ranking-table .el-table__body td:nth-child(n+3) .el-link').should('have.length', 2);
        cy.get('.el-pagination .btn-next').click();
        cy.wait('@ranking').its('request.query').should('include', { start: '20', end: '40' });
        cy.get('.saolei-ranking-table .el-table__body').extractTableData().should((data) => {
            expect(data[0]?.[0]).to.equal('21');
        });
        cy.get('.stat-header[aria-label="Beginner Bvs"]').click();
        cy.wait('@ranking').its('request.query').should('include', { stat: 'bb', start: '0' });
        cy.get('.stat-header[aria-label="Beginner Bvs"]').should('have.attr', 'aria-pressed', 'true');
        cy.get('.stat-header[aria-label="Sum Time"]').should('have.attr', 'aria-pressed', 'false');
        cy.get('.el-pagination .btn-next').click();
        cy.wait('@ranking').its('request.query').should('include', { stat: 'bb', start: '20', end: '40' });
        cy.get('.nf-toggle.el-checkbox').click();
        cy.wait('@ranking').its('request.query').should('include', { board: 'saolei_nf', stat: 'bb', start: '0' });
        cy.get('.el-pagination__sizes .el-select').click();
        cy.get('.el-select-dropdown__item').filter(':visible').contains('50').click();
        cy.wait('@ranking').its('request.query').should('include', { board: 'saolei_nf', stat: 'bb', start: '0', end: '50' });
        cy.get('.stat-header[aria-label="Sum Bvs"]').click();
        cy.wait('@ranking').its('request.query').should('include', { board: 'saolei_nf', stat: 'sumb', start: '0', end: '50' });
    });
});
