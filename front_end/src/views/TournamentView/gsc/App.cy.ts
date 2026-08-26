import App from './App.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { store } from '@/store';
import { pinia } from '@/store/create';
import { LoginStatus } from '@/utils/common/structInterface';
import { TournamentState, TournamentSubclass } from '@/utils/ms_const';
import { Tournament } from '@/utils/tournaments';

const tournamentId = 7;

function gscTournament() {
    return new Tournament({
        id: tournamentId,
        subclass: TournamentSubclass.GSC,
        data: {
            order: 7,
            token: 'G00007',
        },
        start_time: '2000-01-01T00:00:00+08:00',
        end_time: '2099-01-01T00:00:00+08:00',
        state: TournamentState.Normal,
    });
}

function gscParticipantList(participant: boolean) {
    if (!participant) return [];
    return [{
        id: 701,
        token: 'G00007',
        arbiter_identifier_id: 701,
        arbiter_identifier__identifier: 'Player G00007',
        tournament_id: tournamentId,
        user_id: 99,
        start_time: '2000-01-01T00:00:00+08:00',
        end_time: '2099-01-01T00:00:00+08:00',
        rank: null,
        rank_score: 0,
    }];
}

function mountGSC(options: {
    loginStatus: LoginStatus;
    participant: boolean;
}) {
    store.login_status = options.loginStatus;
    if (options.loginStatus === LoginStatus.IsLogin) {
        store.login({ id: 99, username: 'player', realname: 'Player' });
    } else {
        store.logout();
        store.login_status = options.loginStatus;
    }

    cy.intercept('GET', '**/api/tournament/participants*', {
        body: gscParticipantList(options.participant),
    }).as('participantList');
    cy.intercept('GET', '**/api/tournament/get_videos/participant*', {
        body: [],
    }).as('participantVideos');

    cy.mount(App, {
        props: {
            tournament: gscTournament(),
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
}

describe('<GSC App />', () => {
    it('hides real-time score for anonymous users during ongoing tournament', () => {
        mountGSC({ loginStatus: LoginStatus.NotLogin, participant: false });

        cy.contains('Ongoing').should('be.visible');
        cy.contains('Real-Time Score').should('not.exist');
    });

    it('hides real-time score for logged-in users before registration', () => {
        mountGSC({ loginStatus: LoginStatus.IsLogin, participant: false });

        cy.contains('Ongoing').should('be.visible');
        cy.contains('Real-Time Score').should('not.exist');
    });

    it('shows real-time score for registered users', () => {
        mountGSC({ loginStatus: LoginStatus.IsLogin, participant: true });

        cy.contains('Real-Time Score').should('be.visible');
        cy.wait('@participantVideos').its('response.statusCode').should('eq', 200);
    });
});
