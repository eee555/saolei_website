import { createMemoryHistory, createRouter } from 'vue-router';

import TournamentList from './TournamentList.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { serviceConfig } from '@/services/store';
import { local, store } from '@/store';
import { pinia } from '@/store/create';
import { TournamentSeries, TournamentState } from '@/utils/ms_const';
import { Tournament } from '@/utils/tournaments';

const routes = [
    { path: '/tournament', name: 'tournament', component: { template: '<div />' } },
    { path: '/tournament/:id', name: 'tournament_id', component: { template: '<div />' } },
];

function mountTournamentList(tournamentList: Tournament[]) {
    const router = createRouter({
        history: createMemoryHistory(),
        routes,
    });

    void router.push('/tournament');
    cy.wrap(router.isReady()).then(() => {
        cy.mount(TournamentList, {
            props: {
                tournamentList,
            },
            global: {
                plugins: [pinia, router, i18n],
                config: {
                    globalProperties: {
                        $axios,
                    },
                },
            },
        });
    });
    return cy.wrap(router);
}

describe('<TournamentList />', () => {
    beforeEach(() => {
        local.value.language = 'zh-cn';
        i18n.global.locale.value = 'zh-cn';
        serviceConfig.value.userInfoBatchDelay = 0;
        serviceConfig.value.userInfoBatchSize = 100;
        serviceConfig.value.userInfoLastUpdate = 0;
        store.tournamentTabs = [];
        cy.intercept('GET', '**/api/userprofile/avatar/**', { statusCode: 404 });
        cy.intercept('GET', '**/api/userprofile/infobulk*', (req) => {
            const ids = new URL(req.url).searchParams.get('ids')?.split(',').map(Number) ?? [];
            req.reply({
                body: ids.map((id) => ({
                    id,
                    username: `host${id}`,
                    firstname: '',
                    lastname: '',
                    realname: id === 101 ? '主办甲' : '主办乙',
                    is_banned: false,
                    is_staff: false,
                    country: '',
                    signature: '',
                    last_change_avatar: '2026-01-01T00:00:00Z',
                    last_change_signature: '2026-01-01T00:00:00Z',
                    left_avatar_n: 0,
                    left_signature_n: 0,
                })),
            });
        }).as('getUserInfo');
        cy.intercept('GET', '**/api/msuser/records_abstract*', {
            body: {
                b_timems_std: 999999,
                b_bvs_std: 0,
                b_timems_id_std: null,
                b_bvs_id_std: null,
                i_timems_std: 999999,
                i_bvs_std: 0,
                i_timems_id_std: null,
                i_bvs_id_std: null,
                e_timems_std: 999999,
                e_bvs_std: 0,
                e_timems_id_std: null,
                e_bvs_id_std: null,
            },
        });
    });

    it('renders tournament rows with derived display states', () => {
        mountTournamentList([
            new Tournament({
                id: 1,
                name: { zh: '进行中比赛' },
                startDate: new Date(2000, 0, 1, 8, 0, 0),
                endDate: new Date(2099, 0, 1, 8, 0, 0),
                host_id: 101,
                state: TournamentState.Normal,
                series: TournamentSeries.GSC,
            }),
            new Tournament({
                id: 2,
                name: { zh: '已颁奖比赛' },
                startDate: new Date(2026, 0, 1, 8, 0, 0),
                endDate: new Date(2026, 0, 2, 8, 0, 0),
                host_id: 102,
                state: TournamentState.Awarded,
                series: TournamentSeries.GSC,
            }),
        ]);

        cy.contains('进行中比赛').should('be.visible');
        cy.contains('已颁奖比赛').should('be.visible');
        cy.contains('主办甲').should('be.visible');
        cy.contains('主办乙').should('be.visible');
        cy.get('table:visible').getTable().should((tableData) => {
            expect(tableData).to.deep.equal([
                { 状态: '已结束', 比赛: '已颁奖比赛', 主办方: '主办乙', 开始时间: '2026-01-01 08:00:00', 结束时间: '2026-01-02 08:00:00' },
                { 状态: '进行中', 比赛: '进行中比赛', 主办方: '主办甲', 开始时间: '2000-01-01 08:00:00', 结束时间: '2099-01-01 08:00:00' },
            ]);
        });
    });

    it('opens a tournament tab and pushes the tournament route when a row is clicked', () => {
        mountTournamentList([
            new Tournament({
                id: 7,
                name: { zh: '点击打开比赛' },
                host_id: 101,
                state: TournamentState.Normal,
                series: TournamentSeries.GSC,
            }),
        ]).then((router) => {
            cy.contains('.el-table__cell', '点击打开比赛').click();
            cy.then(() => router.currentRoute.value).should((route) => {
                expect(route.name).to.equal('tournament_id');
                expect(route.params.id).to.equal('7');
            });
            cy.wrap(store.tournamentTabs).should((tabs) => {
                expect(tabs).to.have.length(1);
                expect(tabs[0].id).to.equal(7);
            });
        });
    });
});
