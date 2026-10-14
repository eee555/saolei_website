import DensityRanking from './DensityRanking.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { pinia } from '@/store/create';

describe('<DensityRanking />', () => {
    it('preserves backend pagination, formatted scores and cell links', () => {
        cy.mockPlayerNameFallback();
        cy.intercept({ method: 'GET', pathname: '/api/customranking/pluck' }, {
            body: {
                count: 21,
                players: [{ player_id: 42, video_id: 8001, mode: '00', pluck: 0.123456, timems: 1234, bv: 40, upload_time: '2026-10-06T12:00:00Z' }],
            },
        }).as('ranking');
        cy.mount(DensityRanking, { global: { plugins: [i18n, pinia], config: { globalProperties: { $axios } } } });

        cy.wait('@ranking').its('request.query').should('include', { level: 'c8_8_40', start: '0', end: '20' });
        cy.get('.ranking-table tbody').extractTableData().should((data) => {
            expect(data[0]?.[0]).to.equal('1');
            expect(data[0]?.slice(2, 6)).to.deep.equal(['0.123456', 'Standard', '1.234', '40']);
        });
        cy.get('.ranking-table a').should('have.attr', 'href', '#/player/42');
        cy.contains('.ranking-table [data-cy=preview-number]', '0.123456').should('be.enabled');
        cy.get('.pagination .btn-next').click();
        cy.wait('@ranking').its('request.query').should('include', { start: '20', end: '40' });
        cy.get('.ranking-table tbody').extractTableData().should((data) => {
            expect(data[0]?.[0]).to.equal('21');
        });
    });

    it('renders the existing empty message across all seven columns', () => {
        cy.intercept({ method: 'GET', pathname: '/api/customranking/pluck' }, { body: { count: 0, players: [] } }).as('ranking');
        cy.mount(DensityRanking, { global: { plugins: [i18n, pinia], config: { globalProperties: { $axios } } } });
        cy.wait('@ranking');
        cy.get('.ranking-table .base-table-empty').should('have.text', 'No ranking data').and('have.attr', 'colspan', '7');
    });
});
