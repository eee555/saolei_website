import { h, ref } from 'vue';

import AnalyzerLayoutControl from './AnalyzerLayoutControl.vue';
import type { AnalyzerLayout } from './config';

import i18n from '@/i18n';

describe('<AnalyzerLayoutControl />', () => {
    it('starts with a single button and hidden options, opens a focused dropdown, updates the model and closes', () => {
        const layout = ref<AnalyzerLayout | 'auto'>('auto');
        cy.mount({ render: () => h(AnalyzerLayoutControl, { modelValue: layout.value,
            'onUpdate:modelValue': (value) => {
                layout.value = value;
            } }) }, { global: { plugins: [i18n] } });
        cy.get('.video-analyzer-board__layout-control button').should('have.length', 1).and('have.attr', 'aria-expanded', 'false');
        cy.get('.video-analyzer-view__layout-select').should('not.be.visible');
        cy.get('.video-analyzer-board__layout-control button').click();
        cy.get('.video-analyzer-view__layout-select:visible').should('be.focused').find('option').should('have.length', 5);
        cy.get('.video-analyzer-view__layout-select:visible').select('counter-top');
        cy.get('.video-analyzer-board__layout-control button').should('have.attr', 'aria-expanded', 'false').and('be.focused').and(() => {
            expect(layout.value).to.eq('counter-top');
        });
        cy.get('.video-analyzer-view__layout-select').should('have.value', 'counter-top').and('not.be.visible');
        cy.get('.video-analyzer-board__layout-control button').click();
        cy.get('.video-analyzer-view__layout-select:visible').trigger('keydown', { key: 'Escape' });
        cy.get('.video-analyzer-board__layout-control button').should('have.attr', 'aria-expanded', 'false').and('be.focused');
    });
});
