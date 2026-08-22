import App from './App.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { local, store } from '@/store';
import { pinia } from '@/store/create';
import { LoginStatus } from '@/utils/common/structInterface';
import { TournamentState } from '@/utils/ms_const';

const tournamentId = 8;

function weeklyParticipant() {
    return {
        id: 801,
        user_id: 99,
        start_time: '2026-01-01T08:00:00+08:00',
        end_time: '2026-01-01T10:00:00+08:00',
        rank: null,
        rank_score: 0,
        classic_et: [],
        classic_it: [],
        classic_score: 0,
    };
}

function weeklyInfo(registered: boolean) {
    return {
        data: {
            id: tournamentId,
            year: 2099,
            week: 8,
            tournament_format: 'c',
            start_time: '2000-01-01T00:00:00+08:00',
            end_time: '2099-01-01T00:00:00+08:00',
            state: TournamentState.Normal,
        },
        results: null,
        token: registered ? 'WEEKLY-TOKEN' : null,
        participant: registered ? weeklyParticipant() : null,
    };
}

function mountWeekly(options: {
    loginStatus: LoginStatus;
    registered: boolean;
}) {
    local.value.language = 'zh-cn';
    i18n.global.locale.value = 'zh-cn';
    store.login_status = options.loginStatus;
    if (options.loginStatus === LoginStatus.IsLogin) {
        store.login({ id: 99, username: 'player', realname: 'Player' });
    } else {
        store.logout();
        store.login_status = options.loginStatus;
    }

    cy.intercept('GET', '**/api/tournament/weekly/info*', {
        body: weeklyInfo(options.registered),
    }).as('weeklyInfo');
    cy.intercept('GET', '**/api/tournament/get_videos/participant*', {
        body: [],
    }).as('participantVideos');

    cy.mount(App, {
        props: {
            id: tournamentId,
        },
        global: {
            plugins: [pinia, i18n],
            config: {
                globalProperties: {
                    $axios,
                },
            },
        },
    });
    cy.wait('@weeklyInfo').its('response.statusCode').should('eq', 200);
}

describe('<Weekly App />', () => {
    it('hides real-time score for anonymous users during ongoing tournament', () => {
        mountWeekly({ loginStatus: LoginStatus.NotLogin, registered: false });

        cy.contains('进行中').should('be.visible');
        cy.contains('即时成绩').should('not.exist');
    });

    it('hides real-time score for logged-in users before registration', () => {
        mountWeekly({ loginStatus: LoginStatus.IsLogin, registered: false });

        cy.contains('进行中').should('be.visible');
        cy.contains('即时成绩').should('not.exist');
    });

    it('shows real-time score for registered users', () => {
        mountWeekly({ loginStatus: LoginStatus.IsLogin, registered: true });

        cy.contains('即时成绩').should('be.visible');
        cy.wait('@participantVideos').its('response.statusCode').should('eq', 200);
    });
});
