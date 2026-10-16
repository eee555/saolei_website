import { defineComponent, h } from 'vue';
import { createMemoryHistory, createRouter, RouterView } from 'vue-router';

import App from './App.vue';
import UserSettingsView from './UserSettingsView.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { store } from '@/store';
import { pinia } from '@/store/create';

const SummaryStub = defineComponent(() => () => h('div', 'Summary content'));
const RouterRoot = defineComponent({ expose: [], render: () => h(RouterView) });

function mountProfile(path: string, loggedIn = true) {
    if (loggedIn) store.login({ id: 42, username: 'self', realname: 'Self' });
    else store.logout();
    cy.intercept('GET', '/api/userprofile/info/43*', { id: 43, username: 'other', realname: 'Other' });
    cy.intercept('GET', '/api/userprofile/identifier*', ['Owned identifier']).as('identifiers');
    cy.intercept('GET', '/api/userprofile/videolist*', []).as('videos');
    const router = createRouter({
        history: createMemoryHistory(),
        routes: [{
            path: '/player/:id',
            component: App,
            children: [
                { path: 'summary', name: 'user-summary', component: SummaryStub },
                { path: 'settings', name: 'user-settings', component: UserSettingsView },
            ],
        }],
    });
    void router.push(path);
    cy.wrap(router.isReady()).then(() => {
        cy.mount(RouterRoot, {
            global: {
                plugins: [i18n, pinia, router],
                stubs: { Avatar: true },
                config: { globalProperties: { $axios } },
            },
        });
    });
    return router;
}

describe('Profile settings navigation', () => {
    it('opens the settings route from Edit Profile and renders the form and identifiers inline', () => {
        const router = mountProfile('/player/42/summary');
        cy.contains('button', 'Edit Profile').click();
        cy.wrap(router).its('currentRoute.value.name').should('eq', 'user-settings');
        cy.wait('@videos');
        cy.wait('@identifiers');
        cy.get('.user-settings').should('contain.text', 'Local Name').and('contain.text', 'Owned identifier');
        cy.get('.user-settings').contains('Local Name').parent().next().find('input').should('have.value', 'Self');
        cy.get('.el-dialog').should('not.exist');
    });

    for (const loggedIn of [true, false]) {
        it(`redirects ${loggedIn ? 'another player' : 'a guest'} away from settings`, () => {
            const router = mountProfile('/player/43/settings', loggedIn);
            cy.wrap(router).its('currentRoute.value.name').should('eq', 'user-summary');
            cy.get('.user-settings').should('not.exist');
            cy.contains('.el-tabs__item', 'Settings').should('not.exist');
            cy.contains('button', 'Edit Profile').should('not.exist');
        });
    }
});
