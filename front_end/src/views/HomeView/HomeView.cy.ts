import * as ELIcons from '@element-plus/icons-vue';
import PrimeVue from 'primevue/config';

import HomeApp from './App.vue';

import i18n from '@/i18n';
import { serviceConfig } from '@/services/store';

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

const newsQueueResponse = [
    JSON.stringify(validTimeNews),
    JSON.stringify(validBvsNews),
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

const routeResponses = {
    '/video/newest_queue/': newestQueueResponse,
    '/video/news_queue/': newsQueueResponse,
    '/api/video/review_queue': reviewQueueResponse,
};

const users = new Map([
    [7, { id: 7, username: 'player7', realname: 'Player Seven', firstname: 'Player', lastname: 'Seven' }],
    [8, { id: 8, username: 'player8', realname: 'Player Eight', firstname: 'Player', lastname: 'Eight' }],
    [9, { id: 9, username: 'player9', realname: 'Player Nine', firstname: 'Player', lastname: 'Nine' }],
    [10, { id: 10, username: 'player10', realname: 'Player Ten', firstname: 'Player', lastname: 'Ten' }],
]);

function createAxiosGetMock(routes: Record<string, unknown> = routeResponses): sinon.SinonStub {
    const axiosGet = Cypress.sinon.stub();
    axiosGet.callsFake((url: string) => {
        if (!(url in routes)) {
            throw new Error(`Unexpected HomeView API request: ${url}`);
        }
        return Promise.resolve({ data: routes[url] });
    });
    return axiosGet;
}

function mountGlobal(axiosGet: sinon.SinonStub): any {
    return {
        plugins: [i18n, PrimeVue],
        components: ELIcons,
        config: {
            globalProperties: {
                $axios: {
                    defaults: { baseURL: '' },
                    get: axiosGet,
                },
            },
        },
    };
}

function mockUserProfileRequests() {
    cy.intercept('GET', '**/api/userprofile/avatar/**', { statusCode: 404 });
    cy.intercept('GET', '**/api/userprofile/infoupdated*', { body: [] });
    cy.intercept('GET', '**/api/userprofile/infobulk*', (req) => {
        const ids = new URL(req.url).searchParams.get('ids')?.split(',').map(Number) ?? [];
        req.reply({
            body: ids.map((id) => users.get(id) ?? {
                id,
                username: `player${id}`,
                realname: `Player ${id}`,
                firstname: 'Player',
                lastname: String(id),
            }),
        });
    });
}

function configureUserInfoService() {
    serviceConfig.value.userInfoBatchDelay = 0;
    serviceConfig.value.userInfoBatchSize = 100;
    serviceConfig.value.userInfoLastUpdate = 0;
}

function mountHomeApp(axiosGet: sinon.SinonStub) {
    cy.mount(HomeApp, { global: mountGlobal(axiosGet) });
}

function getRouteCalls(axiosGet: sinon.SinonStub, url: string) {
    return axiosGet.getCalls().filter((call) => String(call.args[0]) === url);
}

function expectUrlRequested(axiosGet: sinon.SinonStub, url: string, params?: unknown) {
    const routeCalls = getRouteCalls(axiosGet, url);
    expect(routeCalls.length, `${url} calls`).to.be.greaterThan(0);
    if (params !== undefined) {
        expect(routeCalls[0].args[1]).to.deep.equal(params);
    }
}

describe('HomeView components', () => {
    beforeEach(() => {
        configureUserInfoService();
        mockUserProfileRequests();
    });

    it('renders the real home queue components in the expected tab layout', () => {
        const axiosGet = createAxiosGetMock();

        mountHomeApp(axiosGet);

        cy.contains('.el-tabs__item', 'News').should('be.visible');
        cy.contains('.el-tabs__item', 'Latest').should('have.class', 'is-active');
        cy.contains('.el-tabs__item', 'Pending').should('be.visible').click();
        cy.contains('table:visible', '9.876').should('be.visible');
        cy.then(() => {
            expectUrlRequested(axiosGet, '/video/news_queue/');
            expectUrlRequested(axiosGet, '/video/newest_queue/');
            expectUrlRequested(axiosGet, '/api/video/review_queue');
        });
    });

    it('loads newest videos from the videomanager newest_queue endpoint', () => {
        const axiosGet = createAxiosGetMock();

        mountHomeApp(axiosGet);

        cy.contains('.el-tabs__item', 'Latest').should('be.visible');
        cy.contains('table:visible', '59.987').should('be.visible');
        cy.contains('table:visible', '151').should('be.visible');
        cy.contains('table:visible', '2.517').should('be.visible');
        cy.contains('table:visible', '40.234').should('be.visible');
        cy.contains('table:visible', '2.038').should('be.visible');
        cy.then(() => {
            expectUrlRequested(axiosGet, '/video/newest_queue/', { params: {} });
        });
    });

    it('loads and filters record news from the videomanager news_queue endpoint', () => {
        const axiosGet = createAxiosGetMock();

        mountHomeApp(axiosGet);

        cy.contains('.el-tabs__item', 'News').should('be.visible');
        cy.contains('Player Seven').should('be.visible');
        cy.contains('.clickable', '59.987').should('be.visible');
        cy.contains('Player Eight').should('be.visible');
        cy.contains('.clickable', '3.235').should('be.visible');
        cy.contains('↑0.135').should('be.visible');
        cy.contains('Player 999').should('not.exist');
        cy.contains('Player 1000').should('not.exist');
        cy.then(() => {
            expectUrlRequested(axiosGet, '/video/news_queue/', { params: {} });
        });
    });

    it('loads pending review videos from the video API review_queue endpoint', () => {
        const axiosGet = createAxiosGetMock();

        mountHomeApp(axiosGet);

        cy.contains('.el-tabs__item', 'Pending').should('be.visible');
        cy.contains('.el-tabs__item', 'Pending').click();
        cy.contains('table:visible', '9.876').should('be.visible');
        cy.contains('table:visible', '31').should('be.visible');
        cy.contains('table:visible', '3.139').should('be.visible');
        cy.contains('table:visible', '65.432').should('be.visible');
        cy.contains('table:visible', '2.308').should('be.visible');
        cy.then(() => {
            expectUrlRequested(axiosGet, '/api/video/review_queue');
        });
    });
});
