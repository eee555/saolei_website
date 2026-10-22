import HistoryImport from './HistoryImport.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { hashRouter, installHashHistoryCleanup } from '@cy/support/hashHistory';

describe('<GSC HistoryImport />', () => {
    installHashHistoryCleanup();

    it('renders anonymous identifiers, exposes deletion only without videos and confirms before deleting', () => {
        cy.mockPlayerNameFallback();
        let deleted = false;
        const participant = { id: 123, user_id: 0, manual_scores: true, arbiter_identifier: 'Anonymous Player', has_videos: false, bt20sum: 1000, it12sum: 2000, et5sum: 3000 };
        cy.intercept('GET', '**/api/tournament/gsc/admin-info?*', { body: { id: 42, order: 19, state: 'a', end_time: '2020-01-01T00:00:00Z' } }).as('historyInfo');
        cy.intercept('GET', '**/api/tournament/gsc/results?*', (request) => {
            expect(request.query.tournament_id).to.equal('42');
            request.reply({ body: deleted ? [] : [participant, { ...participant, id: 124, user_id: 987654, has_videos: true }] });
        }).as('history');
        cy.intercept('DELETE', '**/api/tournament/participant/123', (request) => {
            deleted = true;
            request.reply({ statusCode: 204 });
        }).as('delete');
        cy.mount(HistoryImport, { props: { order: 19 }, global: { plugins: [i18n, hashRouter()], config: { globalProperties: { $axios } } } });
        cy.wait(['@historyInfo', '@history']);
        cy.get('[data-cy=history-participants] table').getTable().should((rows) => {
            expect(rows).to.have.length(2);
            expect(rows[0]).to.include({ 选手: 'Anonymous Player', 成绩来源: '手工', 录像: '无', '总成绩 / ms': '6000' });
            expect(rows[1].选手).to.equal('User#987654');
        });
        cy.get('[data-cy=history-refresh-command]').should('contain.text', 'refresh_tournament_scores 42');
        cy.get('[data-cy=history-delete]').should('have.length', 1).click();
        cy.get('@delete.all').should('have.length', 0);
        cy.get('[data-cy=history-delete-confirm]').click();
        cy.wait('@delete');
        cy.wait(['@historyInfo', '@history']);
        cy.get('[data-cy=history-delete]').should('not.exist');
    });
});
