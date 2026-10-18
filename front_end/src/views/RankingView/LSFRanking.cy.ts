import LSFRanking from './LSFRanking.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { topAxes, topField } from '@/services/topRankingService';
import type { TopAnchors, TopRecords } from '@/services/topRankingService';
import { store } from '@/store';
import { pinia } from '@/store/create';

describe('<LSFRanking />', () => {
    it('renders tiers with equivalent time titles and requests the selected ranking and page', () => {
        const records: TopRecords = {};
        const anchors: TopAnchors = {};
        for (const nf of [false, true]) {
            for (const { level, stat } of topAxes) {
                const field = topField(nf, level, stat);
                const value = stat === 't' ? nf ? 60000 : 30000 : 2;
                records[field] = { videos: Array.from({ length: 5 }, (_, id) => ({ value, video_id: id + 1 })) };
                anchors[field] = { value, sample_count: 20 };
            }
        }
        cy.mockPlayerNameFallback();
        cy.then(() => {
            store.topAnchors = null;
        });
        cy.intercept('GET', '**/api/speedranking/top/soft/rank*', {
            count: 21,
            players: [{ player_id: 42, records }],
        }).as('ranking');
        cy.mount(LSFRanking, { global: { plugins: [i18n, pinia], config: { globalProperties: { $axios } } } });
        cy.wait('@ranking').its('request.query').should('include', { ranking: 'lsf', start: '0', end: '20' });
        cy.get('.lsf-ranking-table tbody [data-field=lsf-grade]').should('have.text', '--');
        cy.then(() => {
            store.topAnchors = anchors;
        });
        cy.get('.lsf-ranking-table tbody').extractTableData().should((rows) => {
            expect(rows[0]?.slice(2)).to.deep.equal(['4000.00', ...Array(5).fill('Alien 0.0'), ...Array(4).fill('L. Deity 0.0')]);
        });
        cy.get('.lsf-ranking-table tbody td[title]').should('have.length', 9).each(($cell) => {
            expect($cell.attr('title')).to.equal($cell.attr('data-field')?.startsWith('nf:') === true ? 'Lesser Deity 0.0 (60.000 s)' : 'Alien 0.0 (30.000 s)');
        });
        cy.get('.lsf-ranking-table thead th').should('have.length', 12).eq(3).should('have.text', 'Tier');
        cy.get('.lsf-pagination .btn-next').click();
        cy.wait('@ranking').its('request.query').should('include', { ranking: 'lsf', start: '20', end: '40' });
        cy.get('.lsf-ranking-table tbody tr td').first().should('have.text', '21');
        cy.get('.lsf-ranking-table thead [data-field="nf:sum"]').click();
        cy.wait('@ranking').its('request.query').should('include', { ranking: 'nf:sum', start: '0', end: '20' });
        cy.get('.lsf-ranking-table thead [data-field="nf:sum"]').should('have.attr', 'aria-pressed', 'true');
        cy.get('.lsf-ranking-table thead [data-field="nf:sum"]').closest('th').should('have.attr', 'aria-sort', 'descending');
    });
});
