import App from './App.vue';

import i18n from '@/i18n';
import { videoPlayerConfig, videoplayerstore } from '@/store';
import { hashRouter, installHashHistoryCleanup } from '@cy/support/hashHistory';

describe('Video player dialog', () => {
    installHashHistoryCleanup();
    let previousBackend: typeof videoPlayerConfig.value.backend;

    beforeEach(() => {
        previousBackend = videoPlayerConfig.value.backend;
        videoPlayerConfig.value.backend = 'native';
        videoplayerstore.id = 42;
        videoplayerstore.visible = true;
    });

    afterEach(() => {
        videoplayerstore.visible = false;
        videoPlayerConfig.value.backend = previousBackend;
    });

    it('closes the dialog when following its title link to the analyzer', () => {
        const router = hashRouter({ initialPath: '/' });
        cy.wrap(router.isReady()).then(() => {
            cy.mount(App, { global: { plugins: [i18n, router], stubs: { NativePlayer: true, FlopPlayer: true, StrangeDust: true } } });
        });
        cy.get('.video-player__analyzer-link').should('have.attr', 'href', '#/video/42').and('contain.text', '#42').click();
        cy.hash().should('eq', '#/video/42');
        cy.wrap(videoplayerstore).its('visible').should('eq', false);
        cy.shouldBeAbsentOrHidden('.el-dialog');
    });
});
