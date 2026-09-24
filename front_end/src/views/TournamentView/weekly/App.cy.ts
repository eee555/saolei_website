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
    isStaff?: boolean;
    tournament?: Tournament;
    participants?: TournamentParticipantResponse[];
}) {
    const requestCounts = {
        participantList: 0,
    };
    store.login_status = options.loginStatus;
    if (options.loginStatus === LoginStatus.IsLogin) {
        store.login({ id: 99, username: 'player', realname: options.realname ?? 'Player', is_staff: options.isStaff });
    } else {
        store.logout();
        store.login_status = options.loginStatus;
    }

    cy.intercept('GET', '**/api/tournament/participants*', (req) => {
        requestCounts.participantList += 1;
        req.reply({
            body: options.participants ?? weeklyParticipantList(options.registered),
        });
    }).as('participantList');
    cy.intercept('GET', '**/api/tournament/get_videos/participant*', {
        body: [],
    }).as('participantVideos');

    cy.mount(App, {
        props: {
            tournament: options.tournament ?? weeklyTournament(),
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
    if ((options.tournament ?? weeklyTournament()).getDisplayState() === TournamentState.Ongoing) {
        cy.wait('@participantList').its('response.statusCode').should('eq', 200);
    }
    return requestCounts;
}

describe('<Weekly App />', () => {
    beforeEach(() => {
        cy.mockPlayerNameFallback();
    });

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
        cy.get('[data-cy=weekly-participants]').should('contain', 'NEW-WEEKLY-TOKEN');
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

    for (const loginStatus of [LoginStatus.NotLogin, LoginStatus.IsLogin]) {
        it(`shows all participants without actions for login status ${loginStatus}`, () => {
            mountWeekly({
                loginStatus,
                registered: false,
                participants: [weeklyParticipant({ user_id: 101 }), weeklyParticipant({ id: 802, user_id: 102, token: 'OTHER-TOKEN' })],
            });

            cy.get('[data-cy=weekly-participants] tbody').extractTableData().should('deep.equal', [
                ['User#101', '2026-01-01 08:00:00 ~ 2026-01-01 10:00:00', 'WEEKLY-TOKEN'],
                ['User#102', '2026-01-01 08:00:00 ~ 2026-01-01 10:00:00', 'OTHER-TOKEN'],
            ]);
            cy.get('[data-cy=delete-participant]').should('not.exist');
            cy.contains('[data-cy=weekly-participants] th', 'Actions').should('not.exist');
            cy.get('[data-cy=tournament-data-tabs] [id=tab-participants]').should('have.class', 'is-active');
        });
    }

    for (const role of ['host', 'staff'] as const) {
        it(`lets the ${role} confirm deletion and removes only that participant locally`, () => {
            const tournament = weeklyTournament();
            tournament.hostId = role === 'host' ? 99 : 100;
            const requestCounts = mountWeekly({
                loginStatus: LoginStatus.IsLogin,
                registered: false,
                tournament,
                isStaff: role === 'staff',
                participants: [weeklyParticipant({ user_id: 101 }), weeklyParticipant({ id: 802, user_id: 102, token: 'OTHER-TOKEN' })],
            });
            cy.intercept('DELETE', '**/api/tournament/participant/801', { statusCode: 204 }).as('deleteParticipant');

            cy.get('[data-cy=delete-participant]').first().click();
            cy.contains('.el-dialog', 'Delete this participant?').should('be.visible');
            cy.get('@deleteParticipant.all').should('have.length', 0);
            cy.contains('.el-dialog button', 'Cancel').click();
            cy.get('@deleteParticipant.all').should('have.length', 0);
            cy.get('[data-cy=weekly-participants] tbody tr').should('have.length', 2);

            cy.get('[data-cy=delete-participant]').first().click();
            cy.contains('.el-dialog button', 'Confirm').click();
            cy.wait('@deleteParticipant');
            cy.get('[data-cy=weekly-participants] tbody').extractTableData().should('deep.equal', [
                ['User#102', '2026-01-01 08:00:00 ~ 2026-01-01 10:00:00', 'OTHER-TOKEN', ''],
            ]);
            cy.contains('.el-dialog', 'Delete this participant?').should('not.be.visible');
            cy.then(() => expect(requestCounts.participantList).to.equal(1));
        });
    }

    it('keeps the participant and displays an error when deletion fails', () => {
        mountWeekly({ loginStatus: LoginStatus.IsLogin, registered: true, isStaff: true });
        cy.intercept('DELETE', '**/api/tournament/participant/801', { statusCode: 403 }).as('deleteParticipant');

        cy.get('[data-cy=delete-participant]').click();
        cy.contains('.el-dialog button', 'Confirm').click();
        cy.wait('@deleteParticipant');

        cy.get('.el-notification--error').should('be.visible');
        cy.get('[data-cy=weekly-participants] tbody tr').should('have.length', 1);
        cy.contains('Real-Time Score').should('be.visible');
        cy.contains('.el-dialog button', 'Confirm').should('not.be.disabled');
    });

    it('clears the current session when staff deletes their own participant', () => {
        mountWeekly({ loginStatus: LoginStatus.IsLogin, registered: true, isStaff: true });
        cy.wait('@participantVideos');
        cy.intercept('DELETE', '**/api/tournament/participant/801', { statusCode: 204 }).as('deleteParticipant');

        cy.get('[data-cy=delete-participant]').click();
        cy.contains('.el-dialog button', 'Confirm').click();
        cy.wait('@deleteParticipant');

        cy.get('[data-cy=weekly-participants] tbody tr').should('not.exist');
        cy.contains('Real-Time Score').should('not.exist');
        cy.get('[data-cy=weekly-participant-window]').should('not.exist');
        cy.contains('button', 'Start my session').should('be.enabled');
    });

    it('hides participants before the tournament and loads them after the window ends', () => {
        const tournament = weeklyTournament();
        tournament.startDate = new Date('2098-01-01T00:00:00+08:00');
        mountWeekly({ loginStatus: LoginStatus.NotLogin, registered: false, tournament });
        cy.get('[data-cy=weekly-participants]').should('not.exist');
        cy.get('@participantList.all').should('have.length', 0);

        cy.get<ComponentWrapper<typeof App>>('@vue').then((wrapper) => {
            const finishedTournament = weeklyTournament();
            finishedTournament.endDate = new Date('2001-01-01T00:00:00+08:00');
            return wrapper.setProps({ tournament: finishedTournament });
        });
        cy.wait('@participantList');
        cy.get('[data-cy=weekly-participants]').should('be.visible');
        cy.get('@participantList.all').should('have.length', 1);
    });
});
