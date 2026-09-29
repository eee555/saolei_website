import PrimeVue from 'primevue/config';
import { reactive } from 'vue';

import UserVideoView from './UserVideoView.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { store, VideoListConfig } from '@/store';
import { pinia } from '@/store/create';
import { MS_Mode } from '@/utils/ms_const';
import { UserProfile } from '@/utils/userprofile';

function mountUserVideos(userId = 99, hiddenStates = [true, false]) {
    store.login({ id: 99, username: 'player', realname: 'Player' });
    VideoListConfig.value.profile = ['time'];
    const user = reactive(new UserProfile({ id: userId }));
    cy.intercept('GET', '**/api/userprofile/videolist*', {
        body: hiddenStates.map((hidden, index) => ({
            id: 101 + index,
            level: 'e',
            mode: MS_Mode.Standard,
            software: 'e',
            timems: 40000,
            bv: 100,
            ongoing_tournament: hidden,
        })),
    }).as('videos');
    cy.intercept('GET', '**/api/video/preview*', { statusCode: 404 }).as('preview');
    cy.mount(UserVideoView, {
        props: { user },
        global: { plugins: [pinia, i18n, PrimeVue], config: { globalProperties: { $axios } } },
    });
    cy.wait('@videos');
    // VideoList loads its data columns asynchronously, after rows may already exist.
    cy.get('.p-datatable-table').contains('Time');
    if (userId === 99) cy.get('.p-datatable-table').contains('Action');
    cy.get('.p-datatable-table').extractTableData().should('deep.equal', userId === 99
        ? [['Time', 'Action'], ['40.000', ''], ['40.000', '']]
        : [['Time'], ['40.000'], ['40.000']]);
    return user;
}

function openActions(videoId: number) {
    cy.get(`[data-cy=video-row-actions][data-video-id="${videoId}"]`).click();
    cy.get('[data-tippy-root] [data-cy=reveal-video]:visible').should('be.visible');
}

describe('<UserVideoView /> video reveal', () => {
    it('opens actions in a popover, confirms reveal and updates only the selected video', () => {
        const user = mountUserVideos();
        cy.intercept('POST', '**/api/tournament/video/101/reveal', { statusCode: 204 }).as('reveal');
        cy.get('[data-cy=reveal-video]:visible').should('not.exist');
        openActions(101);
        cy.get('@preview.all').should('have.length', 0);
        cy.get('[data-cy=reveal-video]:visible').click();
        cy.contains('.el-dialog', 'It will still count in all its tournaments.').should('be.visible');
        cy.get('@reveal.all').should('have.length', 0);
        cy.contains('.el-dialog button', 'Cancel').click();
        openActions(101);
        cy.get('[data-cy=reveal-video]:visible').click();
        cy.contains('.el-dialog button', 'Confirm').click();
        cy.wait('@reveal');
        cy.contains('.el-dialog', 'It will still count in all its tournaments.').should('not.be.visible');
        cy.closeElNotifications();
        openActions(101);
        cy.get('[data-cy=reveal-video]:visible').should('be.disabled');
        cy.get('@videos.all').should('have.length', 1);
        cy.get('@preview.all').should('have.length', 0);
        cy.then(() => {
            expect(user.videos?.[0].ongoing_tournament).to.equal(false);
        });
    });

    it('keeps the video hidden on failure and allows retrying', () => {
        const user = mountUserVideos();
        cy.intercept('POST', '**/api/tournament/video/101/reveal', { statusCode: 403 }).as('reveal');
        openActions(101);
        cy.get('[data-cy=reveal-video]:visible').click();
        cy.contains('.el-dialog button', 'Confirm').click();
        cy.wait('@reveal');
        cy.get('.el-notification--error').should('be.visible');
        cy.closeElNotifications();
        cy.contains('.el-dialog button', 'Confirm').should('be.enabled').and('not.have.class', 'is-loading');
        cy.then(() => {
            expect(user.videos?.[0].ongoing_tournament).to.equal(true);
        });
    });

    it('shares one dialog between rows and reveals the last selected video', () => {
        const user = mountUserVideos(99, [true, true]);
        cy.intercept('POST', '**/api/tournament/video/102/reveal', { statusCode: 204 }).as('revealSecond');
        openActions(101);
        cy.get('[data-cy=reveal-video]:visible').click();
        cy.get('.el-dialog').should('have.length', 1);
        cy.contains('.el-dialog button', 'Cancel').click();
        openActions(102);
        cy.get('[data-cy=reveal-video]:visible').click();
        cy.get('[data-cy=reveal-video]:visible').should('not.exist');
        cy.get('.el-dialog').should('have.length', 1);
        cy.contains('.el-dialog button', 'Confirm').click();
        cy.wait('@revealSecond');
        cy.then(() => {
            expect(user.videos?.map((video) => video.ongoing_tournament)).to.deep.equal([true, false]);
        });
        cy.closeElNotifications();
    });

    it('disables revealing an already public video', () => {
        mountUserVideos();
        openActions(102);
        cy.get('[data-cy=reveal-video]:visible').should('be.disabled');
    });

    it('does not expose the actions column on another profile even for staff', () => {
        mountUserVideos(100, [false, false]);
        cy.then(() => {
            store.user.is_staff = true;
        });
        cy.get('[data-cy=video-row-actions]').should('not.exist');
        cy.contains('th', 'Action').should('not.exist');
    });
});
