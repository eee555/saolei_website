import DensityRanking from './DensityRanking.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { pinia } from '@/store/create';
import { hashRouter, installHashHistoryCleanup } from '@cy/support/hashHistory';
import { mockVideoInfo } from '@cy/support/videoInfo';

describe('<DensityRanking />', () => {
    installHashHistoryCleanup();

    it('preserves backend pagination, formatted scores and cell links', () => {
        cy.mockPlayerNameFallback();
        mockVideoInfo([{ id: 8001, level: 'c8_8_40', timems: 1234, bv: 40 }]);
        cy.intercept({ method: 'GET', pathname: '/api/customranking/pluck' }, {
            body: {
                count: 21,
                players: [{ player_id: 42, video_id: 8001, pluck: 0.123456, upload_time: '2026-10-06T12:00:00Z' }],
            },
        }).as('ranking');
        const router = hashRouter();
        cy.mount(DensityRanking, { global: { plugins: [i18n, pinia, router], config: { globalProperties: { $axios } } } });

        cy.wait('@ranking').its('request.query').should('include', { level: 'c8_8_40', start: '0', end: '20' });
        cy.get('.ranking-table tbody').extractTableData().should((data) => {
            expect(data[0]?.[0]).to.equal('1');
            expect(data[0]?.slice(2, 6)).to.deep.equal(['0.123456', 'Standard', '1.234', '40']);
        });
        cy.get('.ranking-table a[href="#/player/42"]').should('exist');
        cy.contains('.ranking-table .video-preview-link', '0.123456').should('have.attr', 'href', '#/video/8001');
        cy.get('.pagination .btn-next').click();
        cy.wait('@ranking').its('request.query').should('include', { start: '20', end: '40' });
        cy.get('.ranking-table tbody').extractTableData().should((data) => {
            expect(data[0]?.[0]).to.equal('21');
        });
        cy.wrap(router).its('currentRoute.value.query').should('deep.equal', { level: 'c8_8_40', page: '2', page_size: '20' });
        cy.get('.board-buttons button').eq(1).click();
        cy.wait('@ranking').its('request.query').should('include', { level: 'c16_16_100', start: '0', end: '20' });
        cy.wrap(router).its('currentRoute.value.query').should('deep.equal', { level: 'c16_16_100', page: '1', page_size: '20' });
        cy.get('@ranking.all').should('have.length', 3);
    });

    it('renders the existing empty message across all seven columns', () => {
        cy.intercept({ method: 'GET', pathname: '/api/customranking/pluck' }, { body: { count: 0, players: [] } }).as('ranking');
        const router = hashRouter({ initialPath: '/ranking/density?level=c24_30_200&page_size=100' });
        cy.wrap(router.isReady()).then(() => {
            cy.mount(DensityRanking, { global: { plugins: [i18n, pinia, router], config: { globalProperties: { $axios } } } });
        });
        cy.wait('@ranking').its('request.query').should('include', { level: 'c24_30_200', start: '0', end: '100' });
        cy.get('.board-buttons button').eq(3).should('have.attr', 'aria-pressed', 'true');
        cy.get('.ranking-table .base-table-empty').should('have.text', 'No ranking data').and('have.attr', 'colspan', '7');
    });
});
