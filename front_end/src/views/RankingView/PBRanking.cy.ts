import PBRanking from './PBRanking.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { pinia } from '@/store/create';

describe('<PBRanking />', () => {
    it('renders metrics, paginates and selects populated BV buckets from the count grids', () => {
        cy.mockPlayerNameFallback();
        const counts: Record<string, number> = {};
        for (const [level, max] of [['b', 54], ['i', 216], ['e', 381]] as const) {
            for (let bv = 1; bv <= max; bv++) {
                if (bv === 2 || (bv >= 10 && bv <= 19)) continue;
                counts[`std:${level}:${bv}`] = 21;
                counts[`nf:${level}:${bv}`] = 7;
            }
        }
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
        cy.get('.pb-ranking-table .el-table__header').extractTableData().should((data) => {
            expect(data[0]).to.deep.equal(['#', 'Player', 'Time', 'Bvs', 'STNB', 'Upload Time']);
        });
        cy.get('.pb-ranking-table .el-table__body').extractTableData().should((data) => {
            expect(data[0]?.[0]).to.equal('1');
            expect(data[0]?.slice(2)).to.deep.equal(['1.000', '1.000', '36.000', '2026-10-05 12:34']);
        });
        cy.get('.pb-pagination .btn-next').click();
        cy.wait('@ranking').its('request.query').should('include', { start: '20', end: '40' });
        cy.get('.pb-ranking-table .el-table__body').extractTableData().should((data) => {
            expect(data[0]?.[0]).to.equal('21');
        });
        cy.get('.nf-toggle.el-checkbox').click();
        cy.wait('@ranking').its('request.query').should('include', { nf: 'true', start: '0' });

        for (const [level, max] of [['b', 54], ['i', 216], ['e', 381]] as const) {
            cy.get(`.pb-level-button[data-level="${level}"]`).click();
            cy.get(`.pb-bv-grid[data-level="${level}"]`).filter(':visible').within(() => {
                cy.get('button').should('have.length', max - 10);
                cy.get('[data-bv="0"]').should('not.exist');
                cy.get('[data-bv="1"]').should('have.text', '7').and('not.be.disabled');
                cy.get('[data-bv="2"]').should('have.text', '0').and('be.disabled');
                cy.get('[data-tens="1"]').should('not.exist');
                cy.get('[data-tens="2"] .pb-bv-label').should('have.text', '2');
                cy.get('button').last().should('have.attr', 'data-bv', String(max));
                cy.get('.pb-bv-header').children().should(($cells) => {
                    expect(Array.from($cells).slice(1).map((cell) => cell.textContent)).to.deep.equal(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']);
                });
                cy.get('.pb-bv-header').should(($header) => {
                    expect(getComputedStyle($header[0]).gridTemplateColumns.split(' ')).to.have.length(11);
                });
                cy.get('.pb-bv-body .pb-bv-header').should('not.exist');
                cy.get(`[data-bv="${max}"]`).scrollIntoView();
                cy.get(`[data-bv="${max}"]`).click();
            });
            cy.wait('@ranking').its('request.query').should('include', { level, bv: String(max), nf: 'true', start: '0' });
            cy.get(`.pb-level-button[data-level="${level}"]`).should('have.attr', 'aria-pressed', 'true').and('have.attr', 'aria-expanded', 'false');
        }
        cy.get('.pb-ranking-table .el-table__body').extractTableData().should((data) => {
            expect(data[0]?.slice(2, 5)).to.deep.equal(['1.000', '381.000', '165735.000']);
        });
        cy.get('.pb-pagination .el-select').click();
        cy.get('.el-select-dropdown__item').filter(':visible').contains('50').click();
        cy.wait('@ranking').its('request.query').should('include', { level: 'e', bv: '381', end: '50', start: '0' });
    });

    it('allows retrying a failed request and displays zero-time derived values as infinity', () => {
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
            body: { count: 1, players: [{ player_id: 42, video_id: 8001, timems: 0, upload_time: '2026-10-05T12:34:00Z' }] },
        }).as('retry');
        cy.get('.pb-toolbar button[aria-label="Refresh"]').click();
        cy.wait('@retry');
        cy.wait('@countsRetry');
        cy.get('.el-alert').should('not.exist');
        cy.get('.pb-ranking-table .el-table__body').extractTableData().should((data) => {
            expect(data[0]?.slice(2, 5)).to.deep.equal(['0.000', 'Infinity', 'Infinity']);
        });
    });
});
