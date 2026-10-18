import { defineComponent, h, shallowRef } from 'vue';

import VideoAnalyzer from './App.vue';
import type { ReplaySource } from './replayParser';

import i18n from '@/i18n';

describe('<VideoAnalyzer /> raw-source interface', () => {
    it('accepts bytes without site requests, keeps instance settings separate and omits absent information', () => {
        cy.viewport(1280, 1000);
        cy.intercept('GET', '**/video/get_software/**', { statusCode: 500 }).as('siteReplay');
        cy.fixture('52200.evf', 'binary').then((binary: string) => {
            const source = shallowRef<ReplaySource>({ data: Uint8Array.from(binary, (character) => character.charCodeAt(0)).buffer, filename: 'local.evf', software: 'e' });
            const colors = { colors: ['#000', '#fff'], thresholds: [50] };
            cy.mount(defineComponent({ expose: [],
                render: () => h('div', { class: 'local-analyzer-test' }, [
                    h('div', { style: { width: '900px', height: '480px' } }, [h(VideoAnalyzer, { source: source.value, probabilityColorScheme: colors, title: 'Local replay' })]),
                    h('div', { style: { width: '900px', height: '480px' } }, [h(VideoAnalyzer, { source: source.value, probabilityColorScheme: colors }, { info: () => [h('span', 'Custom file details')] })]),
                ]) }), { global: { plugins: [i18n] } });
            cy.get('.analyzer-progress-bar__slider').should('have.length', 2).each(($slider) => {
                cy.wrap($slider).should('have.attr', 'max', '10732');
            });
            cy.get('.video-analyzer-view').first().find('.video-analyzer-info').should('not.exist');
            cy.get('.video-analyzer-info').should('have.length', 1).and('have.text', 'Custom file details');
            cy.get('.video-analyzer-view__toolbar').should('not.exist');
            cy.get('.video-analyzer-view h1').should('not.exist');
            cy.get('.video-analyzer-view').first().find('.video-analyzer-board__layout-control button').click();
            cy.get('.video-analyzer-view__layout-select:visible').select('counter-top');
            cy.get('.video-analyzer-view').last().find('.video-analyzer-board__layout-control button').click();
            cy.get('.video-analyzer-view__layout-select:visible').should('have.value', 'auto').trigger('keydown', { key: 'Escape' });
            cy.get('.video-analyzer-counter__settings').first().click();
            cy.get('.video-analyzer-counter__label-width').clear();
            cy.get('.video-analyzer-counter__label-width').type('120');
            cy.get('.video-analyzer-counter__apply').click();
            cy.get('.video-analyzer-counter').first().find('col').first().should('have.css', 'width', '120px');
            cy.get('.video-analyzer-counter').last().find('col').first().should('have.css', 'width', '80px');
            cy.get('.analyzer-progress-bar__slider').first().invoke('val', 5000).trigger('input');
            cy.get('.analyzer-progress-bar__range-start').first().click();
            cy.get('.analyzer-progress-bar__slider').last().should('have.value', '0');
            cy.then(() => {
                source.value = { ...source.value };
            });
            cy.get('.analyzer-progress-bar__slider').first().should('have.value', '0');
            cy.get('.analyzer-progress-bar__range-time').first().should('have.text', '[0.000, 10.732] s');
            cy.get('@siteReplay.all').should('have.length', 0);
        });
    });
});
