import TopSummary from './TopSummary.vue';

import i18n from '@/i18n';
import { topAxes, topField } from '@/services/topRankingService';
import type { TopAnchors, TopRecords } from '@/services/topRankingService';
import { pinia } from '@/store/create';

const records: TopRecords = Object.fromEntries(topAxes.flatMap(({ level, stat }, axis) => [false, true].map((nf) => {
    const mean = (stat === 't' ? 1000 : 1) * (nf ? 3 : 2);
    return [topField(nf, level, stat), { mean, videos: Array.from({ length: 5 }, (_, position) => ({ value: mean, video_id: (nf ? 1000 : 0) + axis * 10 + position + 1 })) }];
})));
const anchors: TopAnchors = Object.fromEntries(topAxes.flatMap(({ level, stat }) => [false, true].map((nf) => [topField(nf, level, stat), { value: stat === 't' ? nf ? 2000 : 1000 : nf ? 1 : 2, sample_count: 20 }])));

describe('<TopSummary />', () => {
    it('shares records between ordinary and NF panels and ignores inactive users', () => {
        cy.intercept('GET', '**/api/speedranking/top/player/42', records).as('records');
        cy.intercept('GET', '**/api/speedranking/top/anchors', anchors).as('anchors');
        cy.intercept('GET', '**/api/speedranking/top/player/43', records).as('other');
        cy.mount(TopSummary, { props: { userId: 42 }, global: { plugins: [i18n, pinia] } });
        cy.wait('@records');
        cy.wait('@anchors');
        cy.get('.top-radar').should('have.length', 2);
        for (const nf of [false, true]) {
            cy.get(`.top-record-table[data-nf="${nf}"] tbody tr`).should('have.length', 9);
            cy.get(`.top-record-table[data-nf="${nf}"] tbody th[scope=rowgroup]`).should('have.length', 3).each(($cell) => {
                expect($cell.attr('rowspan')).to.equal('3');
            });
            cy.get(`.top-record-table[data-nf="${nf}"] tbody`).extractTableData().should((data) => {
                expect(data[0]?.slice(-6)).to.deep.equal(Array(6).fill(nf ? '3.000' : '2.000'));
                expect(data[2]?.slice(-6)).to.deep.equal(Array(6).fill(nf ? '108.000' : '72.000'));
            });
            cy.get(`.top-record-table[data-nf="${nf}"] [data-field=bt] a`).first().should('have.attr', 'href', `#/video/${nf ? 1001 : 1}`);
        }
        cy.get('.top-radar[data-nf=true] .top-radar-mark').should(($mark) => {
            expect($mark.text().trim()).to.equal('NF');
        }).and('be.visible');
        cy.get('@records.all').should('have.length', 1);
        cy.get('@anchors.all').should('have.length', 1);
        cy.get<ComponentWrapper<typeof TopSummary>>('@vue').then((wrapper) => wrapper.setProps({ active: false, userId: 43 }));
        cy.get('.top-radar').should('not.exist');
        cy.get('.top-record-table').should('not.exist');
        cy.get('@other.all').should('have.length', 0);
        cy.get<ComponentWrapper<typeof TopSummary>>('@vue').then((wrapper) => wrapper.setProps({ active: true }));
        cy.wait('@other');
        cy.get('.top-radar').should('have.length', 2);
        cy.get('@anchors.all').should('have.length', 1);
    });

    it('retries a failed anchor request without substituting a false empty result', () => {
        const incomplete = { 'std:bt': { mean: (1000 + 4 * 999999) / 5, videos: [{ value: 1000, video_id: 1 }] } };
        cy.intercept('GET', '**/api/speedranking/top/player/42', incomplete).as('records');
        cy.intercept('GET', '**/api/speedranking/top/anchors', { statusCode: 500 }).as('failed');
        cy.mount(TopSummary, { props: { userId: 42 }, global: { plugins: [i18n, pinia] } });
        cy.wait('@records');
        cy.wait('@failed');
        cy.get('[role=alert]').should('contain.text', 'Could not load top anchors');
        cy.get('.top-radar').should('not.exist');
        cy.get('.top-record-table').should('have.length', 2);
        cy.get('.top-record-table[data-nf=false] tbody tr').should('have.length', 9);
        cy.get('.top-record-table[data-nf=false] tbody').extractTableData().should((data) => {
            expect(data[0]?.slice(-6)).to.deep.equal(['800.199', '1.000', '999.999', '999.999', '999.999', '999.999']);
        });
        cy.get('.top-record-table[data-nf=true] tbody').extractTableData().should((data) => {
            expect(data[0]?.slice(-6)).to.deep.equal(Array(6).fill('999.999'));
            expect(data[2]?.slice(-6)).to.deep.equal(Array(6).fill('0.000'));
        });
        cy.intercept('GET', '**/api/speedranking/top/anchors', anchors).as('retry');
        cy.get('[data-cy=refresh-top]').should('have.attr', 'aria-label', 'Refresh').click();
        cy.wait('@retry');
        cy.get('[role=alert]').should('not.exist');
        cy.get('.top-radar').should('have.length', 2);
    });
});
