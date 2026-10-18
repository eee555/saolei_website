import TopRanking from './TopRanking.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { pinia } from '@/store/create';

const global = { plugins: [i18n, pinia], config: { globalProperties: { $axios } } };

describe('<TopRanking />', () => {
    beforeEach(() => {
        cy.mockPlayerNameFallback();
    });

    it('sorts nine means and independently selects five video details', () => {
        const records = {
            'std:bt': { mean: (1000 + 4 * 999999) / 5, videos: [{ value: 1000, video_id: 8001 }] },
            'std:bb': { mean: 2, videos: [] },
            'std:bs': { mean: 2, videos: [{ value: 10, video_id: 8201 }] },
            'std:et': { mean: 3000, videos: Array.from({ length: 5 }, (_, index) => ({ value: (index + 1) * 1000, video_id: 8101 + index })) },
            'nf:bt': { mean: 4000, videos: [] },
            'nf:bs': { mean: 3, videos: [{ value: 15, video_id: 8301 }] },
        };
        cy.intercept({ method: 'GET', pathname: '/api/speedranking/top/rank' }, { count: 21, players: [{ player_id: 42, records }] }).as('ranking');
        cy.mount(TopRanking, { global });
        cy.wait('@ranking').its('request.query').should('include', { level: 'e', stat: 't', nf: 'false', start: '0', end: '20' });
        cy.get('.top-ranking-table tbody tr').should('have.length', 1).find('td').should('have.length', 16);
        cy.get('.top-detail-toggle').should('have.length', 9).find('.pi-eye').should('have.length', 9);
        cy.get('.top-detail-toggle[aria-pressed=true]').should('have.length', 1).and('have.attr', 'data-detail-field', 'et');
        cy.get('.top-ranking-table thead [data-field=et]').should('have.attr', 'aria-pressed', 'true');
        cy.get('.top-ranking-table tbody').extractTableData().should((data) => {
            expect(data[0]?.slice(2, 11)).to.deep.equal(['800.199', '2.000', '72.000', '999.999', '0.000', '0.000', '3.000', '0.000', '0.000']);
            expect(data[0]?.slice(11)).to.deep.equal(['1.000', '2.000', '3.000', '4.000', '5.000']);
        });
        cy.get('.top-detail-cell a').each(($link, index) => {
            expect($link.attr('href')).to.equal(`#/video/${8101 + index}`);
        });
        cy.get('.top-ranking-table tbody .top-detail-start').should('have.css', 'border-left-style', 'double');
        cy.get('.top-detail-toggle[data-detail-field=bt]').click();
        cy.get('.top-detail-toggle[aria-pressed=true]').should('have.length', 1).and('have.attr', 'data-detail-field', 'bt');
        cy.get('.top-ranking-table thead [data-field=et]').should('have.attr', 'aria-pressed', 'true');
        cy.get('.top-detail-cell a').should('have.length', 1).and('have.attr', 'href', '#/video/8001');
        cy.get('.top-ranking-table tbody').extractTableData().should((data) => {
            expect(data[0]?.slice(11)).to.deep.equal(['1.000', '999.999', '999.999', '999.999', '999.999']);
        });
        cy.get('@ranking.all').should('have.length', 1);
        cy.get('.top-pagination .btn-next').click();
        cy.wait('@ranking').its('request.query').should('include', { level: 'e', stat: 't', start: '20', end: '40' });
        cy.get('.top-detail-toggle[aria-pressed=true]').should('have.length', 1).and('have.attr', 'data-detail-field', 'bt');
        cy.get('.top-ranking-table thead [data-field=bs]').click();
        cy.wait('@ranking').its('request.query').should('include', { level: 'b', stat: 's', start: '0' });
        cy.get('.top-ranking-table thead [data-field=bs]').should('have.attr', 'aria-pressed', 'true').closest('th').should('have.attr', 'aria-sort', 'descending');
        cy.get('.top-detail-toggle[aria-pressed=true]').should('have.length', 1).and('have.attr', 'data-detail-field', 'bs');
        cy.get('.top-ranking-table tbody').extractTableData().should((data) => {
            expect(data[0]?.slice(11)).to.deep.equal(['360.000', '0.000', '0.000', '0.000', '0.000']);
        });
        cy.get('.top-ranking-table thead [data-field=et]').click();
        cy.wait('@ranking').its('request.query').should('include', { level: 'e', stat: 't' });
        cy.get('.top-detail-toggle[aria-pressed=true]').should('have.length', 1).and('have.attr', 'data-detail-field', 'et');
        cy.get('.top-detail-toggle[data-detail-field=bs]').click();
        cy.get('.top-toolbar input[type=checkbox]').check();
        cy.wait('@ranking').its('request.query').should('include', { nf: 'true' });
        cy.get('.top-ranking-table tbody [data-field=bt]').should('have.text', '4.000');
        cy.get('.top-ranking-table tbody [data-field=bs]').should('have.text', '108.000');
        cy.get('.top-detail-toggle[aria-pressed=true]').should('have.length', 1).and('have.attr', 'data-detail-field', 'bs');
        cy.get('.top-detail-cell a').should('have.length', 1).and('have.attr', 'href', '#/video/8301').and('have.text', '540.000');
    });

    it('retries a failed request and handles an empty bucket', () => {
        cy.intercept('GET', '**/api/speedranking/top/rank*', { statusCode: 500 }).as('failed');
        cy.mount(TopRanking, { global });
        cy.wait('@failed');
        cy.get('[role=alert]').should('contain.text', 'Unable to load ranking');
        cy.intercept('GET', '**/api/speedranking/top/rank*', { count: 0, players: [] }).as('retry');
        cy.get('.top-toolbar button[aria-label=Refresh]').click();
        cy.wait('@retry');
        cy.get('[role=alert]').should('not.exist');
        cy.get('.base-table-empty').should('contain.text', 'No records');
    });
});
