import TournamentRanking from './TournamentRanking.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import type { TournamentUserRankField, TournamentUserRankingRow } from '@/services/tournamentService';

function rankingRow(userId: number, init: Partial<TournamentUserRankingRow> = {}): TournamentUserRankingRow {
    return {
        user_id: userId,
        score_current: 12.5,
        last_updated: '2099-01-01T00:00:00Z',
        score_total: 100,
        gsc_total: 60,
        gsc_best: 123456007,
        weekly_total: 40,
        weekly_classic_total: 30,
        weekly_classic_best: 34567802612,
        ...init,
    };
}

function mountTournamentRanking() {
    cy.mount(TournamentRanking, {
        global: {
            plugins: [i18n],
            config: {
                globalProperties: {
                    $axios,
                },
            },
        },
    });
}

function requestQuery(req: { url: string }) {
    const url = new URL(req.url);
    return {
        sortBy: url.searchParams.get('sort_by') as TournamentUserRankField,
        start: Number(url.searchParams.get('start')),
        end: Number(url.searchParams.get('end')),
    };
}

describe('<TournamentRanking />', () => {
    it('renders grouped tournament ranking columns and rows', () => {
        cy.mockPlayerNameFallback();
        cy.intercept('GET', '**/api/tournament/user-ranking*', {
            body: {
                total: 1,
                data: [
                    rankingRow(101),
                ],
            },
        }).as('ranking');

        mountTournamentRanking();

        cy.wait('@ranking').its('request.query').should('include', {
            sort_by: 'score_current',
            start: '0',
            end: '20',
        });
        cy.wait('@playerNameFallbackUserInfoBulk');
        cy.get('body').should(($body) => {
            expect($body.find('.el-loading-mask:visible')).to.have.length(0);
        });
        cy.contains('th', 'Overall').should('have.attr', 'colspan', '2');
        cy.contains('th', 'GSC').should('have.attr', 'colspan', '2');
        cy.contains('th', 'Weekly').should('have.attr', 'colspan', '3');
        cy.get('.ranking-table thead button').should('have.length', 7);
        cy.get('[data-sort-field="score_current"]').should('have.attr', 'aria-pressed', 'true');
        cy.get('.ranking-table thead .caret-wrapper, .ranking-table thead i, .ranking-table thead svg').should('not.exist');
        cy.contains('User#101').should('be.visible');
        cy.get('.ranking-table table').extractTableData().should('deep.equal', [
            ['', '', 'Overall', 'GSC', 'Weekly'],
            ['Current', 'History Total', 'Total', 'Best', 'Total', 'Classic Total', 'Classic Best'],
            ['1', 'User#101', '12.50', '100', '60', '123.456 / GSC#7', '40', '30', '345.678 / 2026-W12'],
        ]);
    });

    it('resets pagination when selecting another ranking field', () => {
        cy.mockPlayerNameFallback();
        const requests: ReturnType<typeof requestQuery>[] = [];
        cy.intercept('GET', '**/api/tournament/user-ranking*', (req) => {
            const query = requestQuery(req);
            requests.push(query);
            req.reply({
                body: {
                    total: 45,
                    data: [
                        rankingRow(query.start + 101, {
                            score_current: query.sortBy === 'gsc_best' ? 20 : 10,
                        }),
                    ],
                },
            });
        }).as('ranking');

        mountTournamentRanking();
        cy.wait('@ranking');
        cy.contains('.el-pager li', '2').click();
        cy.wait('@ranking');
        cy.get('[data-sort-field="score_current"]').click();
        cy.get('.el-pager li.is-active').should('have.text', '2');
        cy.get('[data-sort-field="weekly_classic_total"]').click();
        cy.wait('@ranking');
        cy.get('.el-pager li.is-active').should('have.text', '1');
        cy.get('[data-sort-field="weekly_classic_total"]').should('have.attr', 'aria-pressed', 'true');
        cy.get('[data-sort-field="score_current"]').should('have.attr', 'aria-pressed', 'false');
        cy.get('[data-sort-field="gsc_best"]').focus();
        cy.realPress('Enter');
        cy.wait('@ranking').its('request.query').should('include', { sort_by: 'gsc_best', start: '0', end: '20' });

        cy.then(() => {
            expect(requests).to.deep.equal([
                { sortBy: 'score_current', start: 0, end: 20 },
                { sortBy: 'score_current', start: 20, end: 40 },
                { sortBy: 'weekly_classic_total', start: 0, end: 20 },
                { sortBy: 'gsc_best', start: 0, end: 20 },
            ]);
        });
    });

    it('renders an empty state spanning all ranking columns', () => {
        cy.intercept('GET', '**/api/tournament/user-ranking*', { body: { total: 0, data: [] } }).as('ranking');
        mountTournamentRanking();
        cy.wait('@ranking');
        cy.contains('.base-table-empty', 'No tournament ranking data').should('have.attr', 'colspan', '9');
    });
});
