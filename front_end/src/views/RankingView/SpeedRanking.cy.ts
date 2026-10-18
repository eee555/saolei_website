import { defineComponent, h } from 'vue';
import { createMemoryHistory, createRouter, RouterView } from 'vue-router';

import RankingApp from './App.vue';
import { rankingRoutes } from './routes';

import $axios from '@/http';
import i18n from '@/i18n';
import { pinia } from '@/store/create';

describe('<SpeedRanking /> child routes', () => {
    it('opens PB directly, switches rankings, follows history and redirects the speed entry', () => {
        function checkImprovementHelp(text: string) {
            cy.get('[data-cy=ranking-improve]').focus();
            cy.get('[data-cy=ranking-improve-content]').should('be.visible').and('contain.text', text).and('contain.text', 'zero effective right clicks');
            cy.get('[data-cy=ranking-improve]').blur();
        }

        cy.intercept('GET', '/api/speedranking/pb/counts', { body: { 'std:b:1': 1 } });
        cy.intercept({ method: 'GET', pathname: '/api/speedranking/pb/rank' }, { body: { count: 0, players: [] } }).as('pb');
        cy.intercept({ method: 'GET', pathname: '/api/speedranking/rank' }, { body: { count: 0, players: [] } }).as('saolei');
        cy.intercept('GET', '**/api/speedranking/top/rank*', { count: 0, players: [] }).as('top');
        cy.intercept('GET', '**/api/speedranking/top/soft/rank*', { count: 0, players: [] }).as('lsf');
        const router = createRouter({
            history: createMemoryHistory(),
            routes: [{ path: '/ranking', component: RankingApp, redirect: '/ranking/speed', children: rankingRoutes }],
        });
        void router.push('/ranking/speed/pb');
        cy.wrap(router.isReady()).then(() => {
            cy.mount(defineComponent({ expose: [], render: () => h(RouterView) }), { global: { plugins: [i18n, pinia, router], config: { globalProperties: { $axios } } } });
        });
        cy.wait('@pb');
        cy.get('.ranking-selector').should('contain.text', 'PB');
        cy.get('.el-tabs__item.is-active').should('have.text', 'Speed');
        cy.get('.pb-ranking-table').should('exist');
        checkImprovementHelp('exactly the selected level and 3BV');

        cy.get('.ranking-selector').click();
        cy.get('.el-select-dropdown__item').filter(':visible').contains('Rule').click();
        cy.wait('@saolei');
        cy.wrap(router).its('currentRoute.value.path').should('eq', '/ranking/speed/saolei');
        cy.get('.ranking-selector').should('contain.text', 'Rule');
        cy.get('.el-tabs__item.is-active').should('have.text', 'Speed');
        cy.get('.saolei-ranking-table').should('exist');
        cy.get('.pb-ranking-table').should('not.exist');
        checkImprovementHelp('Improving a level record automatically updates');

        cy.then(() => {
            router.back();
        });
        cy.wrap(router).its('currentRoute.value.path').should('eq', '/ranking/speed/pb');
        cy.get('.ranking-selector').should('contain.text', 'PB');
        cy.get('.pb-ranking-table').should('exist');

        cy.then(() => router.push({ name: 'ranking_speed' }));
        cy.wait('@lsf');
        cy.wrap(router).its('currentRoute.value.path').should('eq', '/ranking/speed/lsf');
        cy.get('.ranking-selector').should('contain.text', 'LSF');
        cy.get('.lsf-ranking-table').should('exist');
        checkImprovementHelp('Improve your top-five means');

        cy.then(() => router.push({ name: 'ranking_speed_top' }));
        cy.wait('@top');
        checkImprovementHelp('Each metric selects its own best five');
    });
});
