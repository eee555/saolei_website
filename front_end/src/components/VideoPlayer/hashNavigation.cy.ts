import { h } from 'vue';
import { createRouter, createWebHashHistory, RouterLink, RouterView } from 'vue-router';

import VideoPlayer from './App.vue';

import PlayerName from '@/components/PlayerName.vue';
import $axios from '@/http';
import i18n from '@/i18n';
import { videoPlayerConfig, videoplayerstore } from '@/store';

function Page(label: string) {
    return { render: () => h('div', { 'data-cy': 'page' }, label) };
}

describe('hash navigation after opening a replay', () => {
    let previousUrl: string;
    let previousBackend: typeof videoPlayerConfig.value.backend;

    beforeEach(() => {
        previousBackend = videoPlayerConfig.value.backend;
        videoPlayerConfig.value.backend = 'native';
        videoplayerstore.visible = false;
        cy.window().then((window) => {
            previousUrl = window.location.href;
        });
        cy.mockPlayerNameFallback();
    });

    afterEach(() => {
        videoplayerstore.visible = false;
        videoPlayerConfig.value.backend = previousBackend;
        cy.window().then((window) => {
            window.history.replaceState(null, '', previousUrl);
        });
    });

    it('updates the view after a username, replay title and ranking click', () => {
        const router = createRouter({
            history: createWebHashHistory(),
            routes: [
                { path: '/ranking', redirect: '/ranking/speed' },
                { path: '/ranking/speed', component: Page('ranking') },
                { path: '/player/:id', redirect: (to) => `/player/${String(to.params.id)}/top` },
                { path: '/player/:id/top', component: Page('player') },
                { path: '/video/:id', component: Page('video') },
            ],
        });
        void router.push('/ranking');
        cy.wrap(router.isReady()).then(() => {
            cy.mount({
                render: () => h('div', [
                    h(RouterLink, { to: '/ranking', 'data-cy': 'nav-ranking' }, { default: () => 'Ranking' }),
                    h(PlayerName, { userId: 42 }),
                    h(VideoPlayer),
                    h(RouterView),
                ]),
            }, {
                global: {
                    plugins: [i18n, router],
                    config: { globalProperties: { $axios } },
                    stubs: { NativePlayer: true, FlopPlayer: true, StrangeDust: true },
                },
            });
        });

        cy.get('[data-cy=page]').should('have.text', 'ranking');
        cy.contains('a', 'User#42').click();
        cy.get('[data-cy=page]').should('have.text', 'player');
        cy.hash().should('eq', '#/player/42/top');

        cy.then(() => {
            videoplayerstore.id = 42;
            videoplayerstore.visible = true;
        });
        cy.get('.video-player__analyzer-link').should('have.attr', 'href', '#/video/42').click();
        cy.get('[data-cy=page]').should('have.text', 'video');
        cy.hash().should('eq', '#/video/42');
        cy.window().its('history.state.current').should('eq', '/video/42');
        cy.wrap(videoplayerstore).its('visible').should('eq', false);

        cy.get('[data-cy=nav-ranking]').click();
        cy.hash().should('eq', '#/ranking/speed');
        cy.get('[data-cy=page]').should('have.text', 'ranking');
    });
});
