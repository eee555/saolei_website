import App from './App.vue';
import { DonutStub, memoryResponse } from './memory.test-data';

import $axios from '@/http';
import i18n from '@/i18n';

const global = {
    plugins: [i18n],
    config: { globalProperties: { $axios } },
    stubs: { DiskUsage: true, TaskSummary: true, VideoSummary: true, TopAnchors: true, VueUiDonut: DonutStub },
};

describe('Server memory requests', () => {
    it('keeps six stable grid items while asynchronous statistics load', () => {
        cy.intercept('GET', '**/api/monitor/memoryusage', { body: memoryResponse() }).as('memory');
        cy.mount(App, { global });
        cy.wait('@memory');
        cy.get('.server-statistics').should(($layout) => {
            expect(Number($layout.attr('data-layout-version'))).to.be.greaterThan(0);
        });
        cy.get('.server-statistics > [data-statistic-item]').should('have.length', 6);
        cy.get('[data-statistic-item="process"] [data-memory-chart="process"]').should('exist');
        cy.get('[data-statistic-item="redis"] [data-memory-chart="redis"]').should('exist');
    });

    it('uses one response for both cards and keeps both on a failed refresh', () => {
        let requests = 0;
        cy.intercept('GET', '**/api/monitor/memoryusage', (request) => {
            requests++;
            request.reply(requests === 1 ? { body: memoryResponse() } : { statusCode: 500 });
        }).as('memory');
        cy.mount(App, { global });
        cy.wait('@memory').its('request.query').should('deep.equal', {});
        cy.get('[data-memory-chart="process"] .statistics-total').should('contain.text', '3.00 KB');
        cy.get('[data-memory-chart="redis"] .statistics-total').should('contain.text', '1.00 KB');
        cy.get('@memory.all').should('have.length', 1);
        cy.contains('[data-memory-chart="redis"] button', 'Refresh').click();
        cy.wait('@memory');
        cy.get('[role="alert"]').should('have.length', 2).each(($alert) => {
            expect($alert.text()).to.contain('last successful result');
        });
        cy.get('[data-memory-chart="process"] .statistics-total').should('contain.text', '3.00 KB');
        cy.get('[data-memory-chart="redis"] .statistics-total').should('contain.text', '1.00 KB');
        cy.get('[data-memory-chart] button').should('not.be.disabled');
        cy.get('@memory.all').should('have.length', 2);
    });

    it('ends loading after an initial request failure and can retry', () => {
        cy.intercept('GET', '**/api/monitor/memoryusage', { statusCode: 503 }).as('failedMemory');
        cy.mount(App, { global });
        cy.wait('@failedMemory');
        cy.get('[data-memory-chart]').should('have.length', 2).and('have.attr', 'aria-busy', 'false');
        cy.get('[role="alert"]').should('have.length', 2);
        cy.get('.statistics-total').should('not.exist');
        cy.intercept('GET', '**/api/monitor/memoryusage', { body: memoryResponse() }).as('retriedMemory');
        cy.contains('[data-memory-chart="process"] button', 'Refresh').click();
        cy.wait('@retriedMemory');
        cy.get('[role="alert"]').should('not.exist');
        cy.get('.statistics-total').should('have.length', 2);
    });

    it('shows Redis even when complete process memory is unavailable', () => {
        const response = memoryResponse();
        response.memory = { ...response.memory, status: 'unavailable', reason: 'permission_denied', total_bytes: null, groups: null, sampled_at: null, host: null, unreadable_processes: 3 };
        cy.intercept('GET', '**/api/monitor/memoryusage', { body: response }).as('memory');
        cy.mount(App, { global });
        cy.wait('@memory');
        cy.get('[data-memory-chart="process"] [role="alert"]').should('contain.text', 'Permission');
        cy.get('[data-memory-chart="process"] .statistics-total').should('not.exist');
        cy.get('[data-memory-chart="redis"] .statistics-total').should('contain.text', '1.00 KB');
        cy.get('[data-memory-chart="redis"] [role="alert"]').should('not.exist');
    });
});
