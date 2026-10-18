import App from './App.vue';

import i18n from '@/i18n';
import { videoPlayerConfig, videoplayerstore } from '@/store';

describe('Video player dialog', () => {
    let previousUrl: string;
    let previousBackend: typeof videoPlayerConfig.value.backend;

    beforeEach(() => {
        previousBackend = videoPlayerConfig.value.backend;
        videoPlayerConfig.value.backend = 'native';
        videoplayerstore.id = 42;
        videoplayerstore.visible = true;
        cy.window().then((window) => {
            previousUrl = window.location.href;
        });
    });

    afterEach(() => {
        videoplayerstore.visible = false;
        videoPlayerConfig.value.backend = previousBackend;
        cy.window().then((window) => {
            window.history.replaceState(null, '', previousUrl);
        });
    });

    it('closes the dialog when following its title link to the analyzer', () => {
        cy.mount(App, { global: { plugins: [i18n], stubs: { NativePlayer: true, FlopPlayer: true, StrangeDust: true } } });
        cy.get('.video-player__analyzer-link').should('have.attr', 'href', '#/video/42').and('contain.text', '#42').click();
        cy.hash().should('eq', '#/video/42');
        cy.wrap(videoplayerstore).its('visible').should('eq', false);
        cy.shouldBeAbsentOrHidden('.el-dialog');
    });
});
