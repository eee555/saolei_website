import PrimeVue from 'primevue/config';

import $axios from '@/http';
import i18n from '@/i18n';
import { serviceConfig } from '@/services/store';
import { local } from '@/store';
import { TournamentState, TournamentSubclass } from '@/utils/ms_const';

const fixedNow = new Date('2026-07-22T12:00:00Z').getTime();
const fullDay = 86400000;

const newestQueueResponse = {
    101: JSON.stringify({
        state: 'c',
        software: 'e',
        time: '2026-07-22T08:00:00Z',
        player_id: 7,
        level: 'e',
        mode: '00',
        timems: 59987,
        bv: 151,
        cl: 250,
        ce: 170,
    }),
    102: JSON.stringify({
        state: 'd',
        software: 'a',
        time: '2026-07-22T09:00:00Z',
        player_id: 8,
        level: 'i',
        mode: '12',
        timems: 40234,
        bv: 82,
        cl: 140,
        ce: 96,
    }),
};

const validTimeNews = {
    time: '2026-07-22T08:00:00Z',
    player_id: 7,
    video_id: 201,
    index: 'timems',
    mode: 'std',
    level: 'e',
    value: 59987,
    old_value: null,
};

const validBvsNews = {
    time: '2026-07-22T09:00:00Z',
    player_id: 8,
    video_id: 202,
    index: 'bvs',
    mode: 'nf',
    level: 'i',
    value: 3.23456,
    old_value: 3.1,
};

const validSecondsTimeNews = {
    time: '2026-07-22T10:00:00Z',
    player_id: 9,
    video_id: 203,
    index: 'timems',
    mode: 'ng',
    level: 'b',
    value: 48321,
    old_value: 49123,
};

const newsQueueResponse = [
    JSON.stringify(validTimeNews),
    JSON.stringify(validBvsNews),
    JSON.stringify(validSecondsTimeNews),
    '{not json',
    JSON.stringify({ ...validTimeNews, player_id: 999, delta: 1 }),
    JSON.stringify({ ...validBvsNews, player_id: 1000, old_value: '3.1' }),
];

const reviewQueueResponse = [
    {
        id: 301,
        player: 9,
        software: 'e',
        level: 'b',
        mode: '00',
        state: 'a',
        cl: 42,
        ce: 25,
        timems: 9876,
        bv: 31,
        upload_time: '2026-07-22T08:00:00Z',
        end_time: '2026-07-22T08:00:10Z',
    },
    {
        id: 302,
        player: 10,
        software: 'a',
        level: 'e',
        mode: '12',
        state: 'a',
        cl: 260,
        ce: 190,
        timems: 65432,
        bv: 151,
        upload_time: '2026-07-22T09:00:00Z',
        end_time: null,
    },
];

function normalTournamentResponse() {
    return [
        {
            id: 401,
            name: { en: 'Upcoming Cup' },
            subclass: TournamentSubclass.GSC,
            data: { order: 401, token: 'G00401' },
            start_time: new Date(fixedNow + 2 * fullDay + 3 * 3600000 + 4 * 60000 + 5000).toISOString(),
            end_time: new Date(fixedNow + 3 * fullDay).toISOString(),
            state: TournamentState.Normal,
            host_id: 1,
        },
        {
            id: 402,
            name: { en: 'Ongoing Cup' },
            subclass: TournamentSubclass.Weekly,
            data: { year: 2099, week: 42, tournament_format: 'c' },
            start_time: new Date(fixedNow - fullDay).toISOString(),
            end_time: new Date(fixedNow + 3 * 3600000 + 4 * 60000 + 5000).toISOString(),
            state: TournamentState.Normal,
            host_id: 1,
        },
        {
            id: 403,
            name: { en: 'Finished Cup' },
            subclass: TournamentSubclass.GSC,
            data: { order: 403, token: 'G00403' },
            start_time: new Date(fixedNow - 3 * fullDay).toISOString(),
            end_time: new Date(fixedNow - 2 * 3600000 - 3 * 60000 - 4000).toISOString(),
            state: TournamentState.Normal,
            host_id: 1,
        },
    ];
}

const mountGlobal = {
    plugins: [i18n, PrimeVue],
    config: {
        globalProperties: {
            $axios,
        },
    },
};

function mockHomeQueueRequests() {
    cy.intercept({ method: 'GET', pathname: '/video/newest_queue/' }, { body: newestQueueResponse }).as('newestQueue');
    cy.intercept({ method: 'GET', pathname: '/video/news_queue/' }, { body: newsQueueResponse }).as('newsQueue');
    cy.intercept({ method: 'GET', pathname: '/api/video/review_queue' }, { body: reviewQueueResponse }).as('reviewQueue');
    cy.intercept({ method: 'GET', pathname: '/api/tournament/get_list' }, { body: normalTournamentResponse() }).as('normalTournaments');
}

function configureUserInfoService() {
    serviceConfig.value.userInfoBatchDelay = 0;
    serviceConfig.value.userInfoBatchSize = 100;
    serviceConfig.value.userInfoLastUpdate = 0;
}

function mountHomeView() {
    cy.then(() => import('./App.vue')).then(({ default: App }) => {
        cy.mount(App, { global: mountGlobal });
    });
    cy.tick(0);
}

describe('HomeView components', () => {
    beforeEach(() => {
        local.value.language = 'en';
        cy.clock(fixedNow);
        configureUserInfoService();
        mockHomeQueueRequests();
        cy.mockPlayerNameFallback();
    });

    it('renders the real home queue components in the expected tab layout', () => {
        mountHomeView();

        cy.contains('.el-tabs__item', 'News').should('be.visible');
        cy.contains('.normal-tournament-card', 'Active Tournaments').should('be.visible');
        cy.contains('.el-tabs__item', 'Latest').should('have.class', 'is-active');
        cy.wait('@normalTournaments');
        cy.wait('@newsQueue');
        cy.wait('@newestQueue');
        cy.contains('.el-tabs__item', 'Pending').should('be.visible').click();
        cy.wait('@reviewQueue');
        cy.contains('table:visible', '9.876').should('be.visible');
    });

    it('loads newest videos from the videomanager newest_queue endpoint', () => {
        mountHomeView();

        cy.wait('@newestQueue').its('request.query').should('deep.equal', {});
        cy.contains('.el-tabs__item', 'Latest').should('be.visible');
        cy.contains('table:visible', '59.987').should('be.visible');
        cy.contains('table:visible', '151').should('be.visible');
        cy.contains('table:visible', '2.517').should('be.visible');
        cy.contains('table:visible', '40.234').should('be.visible');
        cy.contains('table:visible', '2.038').should('be.visible');
    });

    it('loads and filters record news from the videomanager news_queue endpoint', () => {
        mountHomeView();

        cy.wait('@newsQueue').its('request.query').should('deep.equal', {});
        cy.contains('.el-tabs__item', 'News').should('be.visible');
        cy.contains('User#7').should('be.visible');
        cy.contains('.clickable', '59.987').should('be.visible');
        cy.contains('User#8').should('be.visible');
        cy.contains('.clickable', '3.235').should('be.visible');
        cy.contains('↑0.135').should('be.visible');
        cy.contains('.clickable', '48.321').should('be.visible');
        cy.contains('↓-0.802').should('be.visible');
        cy.contains('User#999').should('not.exist');
        cy.contains('User#1000').should('not.exist');
    });

    it('loads normal tournaments with relative state times beside the news area', () => {
        mountHomeView();

        cy.wait('@normalTournaments').its('request.query').should('deep.equal', { category: 'normal' });
        cy.get('.normal-tournament-card .el-card__header .el-link').first().should('have.attr', 'href', '/#/tournament');
        cy.contains('.normal-tournament-name .el-link', 'Upcoming Cup').
            should('be.visible').
            and('have.attr', 'href', '/#/tournament/401');
        cy.contains('.normal-tournament-name .el-link', 'Ongoing Cup').
            should('be.visible').
            and('have.attr', 'href', '/#/tournament/402');
        cy.contains('.normal-tournament-name .el-link', 'Finished Cup').
            should('be.visible').
            and('have.attr', 'href', '/#/tournament/403');
        cy.contains('.normal-tournament-card .text-warning', 'starts in 2d 03:04:05').should('be.visible');
        cy.contains('.normal-tournament-card .text-danger', 'ends in 03:04:05').should('be.visible');
        cy.contains('.normal-tournament-card .text-success', 'ended 02:03:04 ago').should('be.visible');
        cy.get('.normal-tournament-card .el-card__header .el-link').eq(1).click();
        cy.wait('@normalTournaments').its('request.query').should('deep.equal', { category: 'normal' });
    });

    it('loads pending review videos from the video API review_queue endpoint', () => {
        mountHomeView();

        cy.contains('.el-tabs__item', 'Pending').should('be.visible');
        cy.contains('.el-tabs__item', 'Pending').click();
        cy.wait('@reviewQueue');
        cy.contains('table:visible', '9.876').should('be.visible');
        cy.contains('table:visible', '31').should('be.visible');
        cy.contains('table:visible', '3.139').should('be.visible');
        cy.contains('table:visible', '65.432').should('be.visible');
        cy.contains('table:visible', '2.308').should('be.visible');
    });
});
