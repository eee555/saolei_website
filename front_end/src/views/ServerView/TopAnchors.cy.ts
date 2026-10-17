import TopAnchors from './TopAnchors.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { topAxes, topField } from '@/services/topRankingService';
import { pinia } from '@/store/create';

const anchors = Object.fromEntries(topAxes.flatMap(({ level, stat }) => [false, true].map((nf) => [topField(nf, level, stat), { value: stat === 't' ? 1000 : 1, sample_count: 20 }])));

describe('<TopAnchors />', () => {
    it('renders all anchors with independent units and retains them after a refresh error', () => {
        cy.intercept('GET', '**/api/speedranking/top/anchors', anchors).as('anchors');
        cy.mount(TopAnchors, { global: { plugins: [i18n, pinia], config: { globalProperties: { $axios } } } });
        cy.wait('@anchors');
        cy.get('[data-anchor]').should('have.length', 18);
        cy.get('[data-anchor="std:bt"]').should('have.text', '1.000');
        cy.get('[data-anchor="std:bs"]').should('have.text', '36.000');
        cy.get('[data-anchor="nf:es"]').should('have.text', '435.000');
        cy.get('.anchor-panel').should('have.length', 3);
        cy.get('@anchors.all').should('have.length', 1);
        cy.intercept('GET', '**/api/speedranking/top/anchors', { statusCode: 500 }).as('failed');
        cy.contains('button', 'Refresh').click();
        cy.wait('@failed');
        cy.get('[role=alert]').should('contain.text', 'last successful result');
        cy.get('[data-anchor]').should('have.length', 18);
    });
});
