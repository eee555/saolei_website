import PBRanking from './PBRanking.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { pinia } from '@/store/create';

describe('<PBRanking />', () => {
    it('loads counts, paginates and requests selected NF and BV buckets', () => {
        cy.mockPlayerNameFallback();
        const counts = { 'std:b:1': 21, 'nf:b:54': 7, 'nf:i:216': 7, 'nf:e:381': 7 };
        cy.intercept('GET', '/api/speedranking/pb/counts', { body: counts }).as('counts');
        const upload = new Date(2026, 9, 5, 12, 34, 0).toISOString();
        cy.intercept({ method: 'GET', pathname: '/api/speedranking/pb/rank' }, {
            body: { count: 21, players: [{ player_id: 42, video_id: 8001, timems: 1000, upload_time: upload }] },
        }).as('ranking');
        cy.mount(PBRanking, { global: { plugins: [i18n, pinia], config: { globalProperties: { $axios } } } });
        cy.wait('@ranking').its('request.query').should('include', { level: 'b', bv: '1', nf: 'false', start: '0', end: '20' });
        cy.wait('@counts');
        cy.get('.pb-level-button[data-level="b"]').click();
        cy.get('.pb-bv-grid[data-level="b"]').filter(':visible').find('[data-bv="1"]').should('have.text', '21');
        cy.get('.pb-level-button[data-level="b"]').click();
        cy.get('.pb-pagination .btn-next').click();
        cy.wait('@ranking').its('request.query').should('include', { start: '20', end: '40' });
        cy.get('.pb-ranking-table tbody').extractTableData().should((data) => {
            expect(data[0]?.[0]).to.equal('21');
        });
        cy.get('.nf-toggle.el-checkbox').click();
        cy.wait('@ranking').its('request.query').should('include', { nf: 'true', start: '0' });

        for (const [level, max] of [['b', 54], ['i', 216], ['e', 381]] as const) {
            cy.get(`.pb-level-button[data-level="${level}"]`).click();
            cy.get(`.pb-bv-grid[data-level="${level}"]`).filter(':visible').within(() => {
                cy.get(`[data-bv="${max}"]`).should('have.text', '7');
                cy.get(`[data-bv="${max}"]`).click();
            });
            cy.wait('@ranking').its('request.query').should('include', { level, bv: String(max), nf: 'true', start: '0' });
        }
        cy.get('.pb-pagination .el-select').click();
        cy.get('.el-select-dropdown__item').filter(':visible').contains('50').click();
        cy.wait('@ranking').its('request.query').should('include', { level: 'e', bv: '381', end: '50', start: '0' });
    });

    it('allows retrying failed ranking and count requests', () => {
        cy.mockPlayerNameFallback();
        cy.intercept('GET', '/api/speedranking/pb/counts', { statusCode: 500 }).as('countsFailed');
        cy.intercept({ method: 'GET', pathname: '/api/speedranking/pb/rank' }, { statusCode: 500 }).as('failed');
        cy.mount(PBRanking, { global: { plugins: [i18n, pinia], config: { globalProperties: { $axios } } } });
        cy.wait('@failed');
        cy.wait('@countsFailed');
        cy.get('.el-alert').should('contain.text', 'Unable to load ranking');
        cy.get('.el-alert').should('contain.text', 'Unable to load board counts');
        cy.intercept('GET', '/api/speedranking/pb/counts', { body: { 'std:b:1': 1 } }).as('countsRetry');
        cy.intercept({ method: 'GET', pathname: '/api/speedranking/pb/rank' }, {
            body: { count: 1, players: [{ player_id: 42, video_id: 8001, timems: 1000, upload_time: '2026-10-05T12:34:00Z' }] },
        }).as('retry');
        cy.get('.pb-toolbar button[aria-label="Refresh"]').click();
        cy.wait('@retry');
        cy.wait('@countsRetry');
        cy.get('.el-alert').should('not.exist');
    });
});
