import tinycolor from 'tinycolor2';

import TopRanking from './TopRanking.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { colorThemes } from '@/store/color';
import { pinia } from '@/store/create';
import { hashRouter, installHashHistoryCleanup } from '@cy/support/hashHistory';

function mountTopRanking(initialPath = '/ranking/speed/top') {
    const router = hashRouter({ initialPath });
    cy.wrap(router.isReady()).then(() => {
        cy.mount(TopRanking, { global: { plugins: [i18n, pinia, router], config: { globalProperties: { $axios } } } });
    });
    return router;
}

describe('<TopRanking />', () => {
    installHashHistoryCleanup();

    beforeEach(() => {
        cy.mockPlayerNameFallback();
    });

    it('sorts nine means and independently selects five video details', () => {
        const records = {
            'std:bt': { videos: [{ value: 1000, video_id: 8001 }] },
            'std:bb': { videos: [{ value: 10, video_id: 8200 }] },
            'std:bs': { videos: [{ value: 10, video_id: 8201 }] },
            'std:et': { videos: Array.from({ length: 5 }, (_, index) => ({ value: (index + 1) * 1000, video_id: 8101 + index })) },
            'nf:bt': { videos: Array.from({ length: 5 }, (_, index) => ({ value: 4000, video_id: 8401 + index })) },
            'nf:bs': { videos: [{ value: 15, video_id: 8301 }] },
        };
        cy.intercept({ method: 'GET', pathname: '/api/speedranking/top/rank' }, { count: 21, players: [{ player_id: 42, records }] }).as('ranking');
        const router = mountTopRanking();
        cy.wait('@ranking').its('request.query').should('include', { level: 'e', stat: 't', nf: 'false', start: '0', end: '20' });
        cy.get('.top-ranking-table tbody tr').should('have.length', 1).find('td').should('have.length', 16);
        cy.get('.top-detail-toggle').should('have.length', 9).find('.pi-eye').should('have.length', 9);
        cy.get('.top-detail-toggle[aria-pressed=true]').should('have.length', 1).and('have.attr', 'data-detail-field', 'et');
        cy.get('.top-ranking-table thead [data-field=et]').should('have.attr', 'aria-pressed', 'true');
        cy.get('.top-ranking-table tbody').extractTableData().should((data) => {
            expect(data[0]?.slice(2, 11)).to.deep.equal(['800.199', '2.000', '72.000', '999.999', '0.000', '0.000', '3.000', '0.000', '0.000']);
            expect(data[0]?.slice(11)).to.deep.equal(['1.000', '2.000', '3.000', '4.000', '5.000']);
        });
        cy.get<ComponentWrapper<typeof TopRanking>>('@vue').then((wrapper) => wrapper.setProps({ colored: true }));
        cy.get('.top-ranking-table tbody [data-field=et]').should('have.css', 'background-color', tinycolor(colorThemes.etime.value.getColor(3)).toRgbString());
        cy.get('.top-ranking-table tbody [data-field=bb]').should('have.css', 'background-color', tinycolor(colorThemes.bvs.value.getColor(2)).toRgbString());
        cy.get('.top-ranking-table tbody [data-field=bs]').should('have.css', 'background-color', tinycolor(colorThemes.stnb.value.getColor(72)).toRgbString());
        cy.get('.top-detail-cell').first().should('have.css', 'background-color', tinycolor(colorThemes.etime.value.getColor(1)).toRgbString());
        cy.get<ComponentWrapper<typeof TopRanking>>('@vue').then((wrapper) => wrapper.setProps({ colored: false }));
        cy.get('.top-detail-cell').first().should(($cell) => {
            expect($cell[0].style.backgroundColor).to.equal('');
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
        cy.wrap(router).its('currentRoute.value.query').should('include', { sort: 'et', detail: 'bt', page: '1' });
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
        cy.wrap(router).its('currentRoute.value.query').should('deep.equal', { sort: 'et', detail: 'bs', nf: '1', page: '1', page_size: '20' });
    });

    it('retries a failed request and handles an empty bucket', () => {
        cy.intercept('GET', '**/api/speedranking/top/rank*', { statusCode: 500 }).as('failed');
        mountTopRanking('/ranking/speed/top?sort=ib&detail=bs&nf=1&page_size=50');
        cy.wait('@failed');
        cy.get('.top-ranking-table thead [data-field=ib]').should('have.attr', 'aria-pressed', 'true');
        cy.get('.top-detail-toggle[aria-pressed=true]').should('have.attr', 'data-detail-field', 'bs');
        cy.get('[role=alert]').should('contain.text', 'Unable to load ranking');
        cy.intercept('GET', '**/api/speedranking/top/rank*', { count: 0, players: [] }).as('retry');
        cy.get('@vue').its('vm').invoke('refresh');
        cy.wait('@retry').its('request.query').should('include', { level: 'i', stat: 'b', nf: 'true', start: '0', end: '50' });
        cy.get('[role=alert]').should('not.exist');
        cy.get('.base-table-empty').should('contain.text', 'No records');
    });
});
