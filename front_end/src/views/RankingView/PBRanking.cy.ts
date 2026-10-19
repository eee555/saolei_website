import PBRanking from './PBRanking.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { pinia } from '@/store/create';
import { hashRouter, installHashHistoryCleanup } from '@cy/support/hashHistory';

describe('<PBRanking />', () => {
    installHashHistoryCleanup();

    it('loads counts, paginates and requests selected NF and BV buckets', () => {
        cy.mockPlayerNameFallback();
        const counts = { 'std:b:1': 21, 'nf:e:381': 7 };
        cy.intercept('GET', '/api/speedranking/pb/counts', { body: counts }).as('counts');
        const upload = new Date(2026, 9, 5, 12, 34, 0).toISOString();
        cy.intercept({ method: 'GET', pathname: '/api/speedranking/pb/rank' }, {
            body: { count: 21, players: [{ player_id: 42, video_id: 8001, timems: 1000, upload_time: upload }] },
        }).as('ranking');
        cy.mount(PBRanking, { props: { colored: true }, global: { plugins: [i18n, pinia, hashRouter()], config: { globalProperties: { $axios } } } });
        cy.wait('@ranking').its('request.query').should('include', { level: 'b', bv: '1', nf: 'false', start: '0', end: '20' });
        cy.wait('@counts');
        cy.get<ComponentWrapper<typeof PBRanking>>('@vue').should((wrapper) => {
            expect(wrapper.findComponent({ name: 'PBRankingTable' }).props('colored')).to.equal(true);
        });
        cy.get('.pb-level-button[data-level="b"]').click();
        cy.get('.pb-bv-grid[data-level="b"]').filter(':visible').find('[data-bv="1"]').should('have.text', '21');
        cy.get('.pb-level-button[data-level="b"]').click();
        cy.get('.pb-pagination .btn-next').click();
        cy.wait('@ranking').its('request.query').should('include', { start: '20', end: '40' });
        cy.get('.pb-ranking-table tbody').extractTableData().should((data) => {
            expect(data[0]?.[0]).to.equal('21');
        });
        cy.get('.nf-toggle input[type=checkbox]').should('not.be.checked').focus();
        cy.realPress('Space');
        cy.get('.nf-toggle input[type=checkbox]').should('be.checked');
        cy.wait('@ranking').its('request.query').should('include', { nf: 'true', start: '0' });

        cy.get('.pb-level-button[data-level="e"]').click();
        cy.get('.pb-bv-grid[data-level="e"]').filter(':visible').find('[data-bv="381"]').click();
        cy.wait('@ranking').its('request.query').should('include', { level: 'e', bv: '381', nf: 'true', start: '0' });
        cy.get('.pb-pagination .el-select').click();
        cy.get('.el-select-dropdown__item').filter(':visible').contains('50').click();
        cy.wait('@ranking').its('request.query').should('include', { level: 'e', bv: '381', end: '50', start: '0' });
    });

    it('allows retrying failed ranking and count requests', () => {
        cy.mockPlayerNameFallback();
        cy.intercept('GET', '/api/speedranking/pb/counts', { statusCode: 500 }).as('countsFailed');
        cy.intercept({ method: 'GET', pathname: '/api/speedranking/pb/rank' }, { statusCode: 500 }).as('failed');
        cy.mount(PBRanking, { global: { plugins: [i18n, pinia, hashRouter()], config: { globalProperties: { $axios } } } });
        cy.wait('@failed');
        cy.wait('@countsFailed');
        cy.get('.el-alert').should('contain.text', 'Unable to load ranking');
        cy.get('.el-alert').should('contain.text', 'Unable to load board counts');
        cy.intercept('GET', '/api/speedranking/pb/counts', { body: { 'std:b:1': 1 } }).as('countsRetry');
        cy.intercept({ method: 'GET', pathname: '/api/speedranking/pb/rank' }, {
            body: { count: 1, players: [{ player_id: 42, video_id: 8001, timems: 1000, upload_time: '2026-10-05T12:34:00Z' }] },
        }).as('retry');
        cy.get('@vue').its('vm').invoke('refresh');
        cy.wait('@retry');
        cy.wait('@countsRetry');
        cy.get('.el-alert').should('not.exist');
    });
});
