import App from './App.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import type { TournamentParticipantResponse } from '@/services/tournamentService';
import { store } from '@/store';
import { pinia } from '@/store/create';
import { LoginStatus } from '@/utils/common/structInterface';
import { TournamentState, TournamentSubclass } from '@/utils/ms_const';
import { Tournament } from '@/utils/tournaments';

const tournamentId = 8;

function weeklyTournament() {
    return new Tournament({
        id: tournamentId,
        subclass: TournamentSubclass.Weekly,
        data: {
            year: 2099,
            week: 8,
            tournament_format: 'c',
        },
        start_time: '2000-01-01T00:00:00+08:00',
        end_time: '2099-01-01T00:00:00+08:00',
        state: TournamentState.Normal,
    });
}

function weeklyParticipant(init: Partial<TournamentParticipantResponse> = {}): TournamentParticipantResponse {
    return {
        id: 801,
        token: 'WEEKLY-TOKEN',
        arbiter_identifier__identifier: null,
        tournament_id: tournamentId,
        user_id: 99,
        start_time: '2026-01-01T08:00:00+08:00',
        end_time: '2026-01-01T10:00:00+08:00',
        rank: null,
        rank_score: 0,
        ...init,
    };
}

function weeklyParticipantList(registered: boolean) {
    if (!registered) return [];
    return [weeklyParticipant()];
}

function mountWeekly(options: {
    loginStatus: LoginStatus;
    registered: boolean;
    realname?: string;
}) {
    const requestCounts = {
        participantList: 0,
    };
    store.login_status = options.loginStatus;
    if (options.loginStatus === LoginStatus.IsLogin) {
        store.login({ id: 99, username: 'player', realname: options.realname ?? 'Player' });
    } else {
        store.logout();
        store.login_status = options.loginStatus;
    }

    cy.intercept('GET', '**/api/tournament/participants*', (req) => {
        requestCounts.participantList += 1;
        req.reply({
            body: weeklyParticipantList(options.registered),
        });
    }).as('participantList');
    cy.intercept('GET', '**/api/tournament/get_videos/participant*', {
        body: [],
    }).as('participantVideos');

    cy.mount(App, {
        props: {
            tournament: weeklyTournament(),
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
    cy.wait('@participantList').its('response.statusCode').should('eq', 200);
    return requestCounts;
}

describe('<Weekly App />', () => {
    it('hides real-time score for anonymous users during ongoing tournament', () => {
        mountWeekly({ loginStatus: LoginStatus.NotLogin, registered: false });

        cy.contains('Ongoing').should('be.visible');
        cy.contains('Real-Time Score').should('not.exist');
    });

    it('hides real-time score for logged-in users before registration', () => {
        mountWeekly({ loginStatus: LoginStatus.IsLogin, registered: false });

        cy.contains('Ongoing').should('be.visible');
        cy.contains('Real-Time Score').should('not.exist');
    });

    it('shows real-time score for registered users', () => {
        mountWeekly({ loginStatus: LoginStatus.IsLogin, registered: true });

        cy.contains('Real-Time Score').should('be.visible');
        cy.wait('@participantVideos').its('response.statusCode').should('eq', 200);
    });

    it('uses the registration response without fetching participants again', () => {
        const requestCounts = mountWeekly({ loginStatus: LoginStatus.IsLogin, registered: false });
        cy.intercept('POST', '**/api/tournament/weekly/participant', {
            body: weeklyParticipant({
                id: 802,
                token: 'NEW-WEEKLY-TOKEN',
            }),
        }).as('createWeeklyParticipant');

        cy.contains('button', 'Start my session').click();
        cy.contains('.el-dialog', 'Are you ready?').should('be.visible');
        cy.contains('.el-dialog', 'This action is irreversible').should('be.visible');
        cy.contains('.el-dialog button', 'Confirm').click();

        cy.wait('@createWeeklyParticipant').its('request.body').should('deep.equal', 'id=8');
        cy.contains('NEW-WEEKLY-TOKEN').should('be.visible');
        cy.get('[data-cy=weekly-participant-window]').should('contain', '2026-01-01 08:00:00').and('contain', '2026-01-01 10:00:00');
        cy.contains('Real-Time Score').should('be.visible');
        cy.wait('@participantVideos').its('response.statusCode').should('eq', 200);
        cy.then(() => {
            expect(requestCounts.participantList).to.equal(1);
        });
    });

    it('disables registration for logged-in users without real name', () => {
        const requestCounts = mountWeekly({ loginStatus: LoginStatus.IsLogin, registered: false, realname: '' });
        cy.intercept('POST', '**/api/tournament/weekly/participant', { statusCode: 200, body: {} }).as('createWeeklyParticipant');

        cy.contains('button', 'Start my session').should('be.disabled');
        cy.contains('.el-dialog', 'Are you ready?').should('not.exist');
        cy.contains('Real name required').should('be.visible');
        cy.contains('WEEKLY-TOKEN').should('not.exist');
        cy.contains('Real-Time Score').should('not.exist');
        cy.get('@createWeeklyParticipant.all').should('have.length', 0);
        cy.then(() => {
            expect(requestCounts.participantList).to.equal(1);
        });
    });
});
