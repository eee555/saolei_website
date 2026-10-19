import TopAnchors from './TopAnchors.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { topAxes, topField } from '@/services/topRankingService';
import { store } from '@/store';
import { pinia } from '@/store/create';

const anchors = Object.fromEntries(topAxes.flatMap(({ level, stat }) => [false, true].map((nf) => [topField(nf, level, stat), { value: stat === 't' ? 1000 : 1, sample_count: 20 }])));

describe('<TopAnchors />', () => {
    it('renders the startup anchors with independent units', () => {
        cy.then(() => {
            store.topAnchors = anchors;
        });
        cy.mount(TopAnchors, { global: { plugins: [i18n, pinia], config: { globalProperties: { $axios } } } });
        cy.get('[data-anchor]').should('have.length', 18);
        cy.get('[data-anchor="std:bt"]').should('have.text', '1.000');
        cy.get('[data-anchor="std:bs"]').should('have.text', '36.000');
        cy.get('[data-anchor="nf:es"]').should('have.text', '435.000');
        cy.get('.anchor-panel').should('have.length', 3);
    });
});
