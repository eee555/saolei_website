import { defineComponent, h, reactive } from 'vue';

import PublicTournament from './PublicTournament.vue';

import i18n from '@/i18n';
import { globalNow } from '@/utils/datetime';
import { TournamentState } from '@/utils/ms_const';
import { Tournament, TournamentParticipant } from '@/utils/tournaments';
import type { VideoAbstract } from '@/utils/videoabstract';
import { FakeDirectoryHandle, setDirectoryPicker } from '@cy/support/autoUploader';

function mountTournament(index = 0, state = TournamentState.Normal) {
    const data = reactive({
        tournament: new Tournament({ id: 7, name: 'Test tournament', state, start_time: '2000-01-01', end_time: '2099-01-01' }),
        participants: [new TournamentParticipant({ id: 10, tournament_id: 7, user_id: 99, start_time: new Date('2000-01-01'), end_time: new Date('2099-01-01') })],
        index,
    });
    const refreshParticipants = cy.stub().as('refreshParticipants').resolves();
    const Host = defineComponent({
        setup: () => () => h(PublicTournament<TournamentParticipant>, {
            ...data, loading: false, autoUploaderEnabled: true, autoUploaderFilter: () => true, refreshParticipants,
        }, {
            description: () => h('p', 'Description'),
            participationGuide: () => h('p', 'Registration'),
            autoUploaderFilter: () => h('span', 'Custom filter'),
            allSummary: ({ onParticipantSelect }: { onParticipantSelect: (item: TournamentParticipant) => void }) => h('button', { onClick: () => {
                onParticipantSelect(data.participants[0]);
            } }, 'Player row'),
            personalSummary: ({ videos }: { videos: VideoAbstract[] }) => h('p', { 'data-cy': 'summary-count' }, `Videos: ${videos.length}`),
        }),
    });
    cy.mount(Host, { global: { plugins: [i18n] } });
    return data;
}

describe('<PublicTournament />', () => {
    beforeEach(() => {
        cy.mockPlayerNameFallback();
    });
    afterEach(() => {
        setDirectoryPicker();
    });

    it('shows only the participant tab until registration and separates the two refresh actions', () => {
        cy.intercept('GET', '**/api/tournament/get_videos/participant*', { body: [] }).as('videos');
        const data = mountTournament(-1);
        cy.get('#tab-personal').should('not.exist');
        cy.get('.auto-uploader').should('not.exist');
        cy.contains('Export all video stats').should('not.exist');
        cy.get('[data-cy=participants-refresh]').click();
        cy.get('@refreshParticipants').should('have.been.calledOnce');
        cy.get('@videos.all').should('have.length', 0);

        cy.then(() => {
            data.index = 0;
        });
        cy.wait('@videos');
        cy.get('#tab-personal').click();
        cy.get('[data-cy=summary-count]').should('be.visible');
        cy.get('[data-cy=personal-score-refresh]').click();
        cy.wait('@videos');
        cy.get('@refreshParticipants').should('have.been.calledOnce');
        cy.contains('Management').should('not.exist');
        cy.then(() => {
            data.index = -1;
        });
        cy.get('#tab-personal').should('not.exist');
        cy.get('#tab-participants').should('have.class', 'is-active');
    });

    it('blocks upload while fetching videos and blocks refresh while watching, across tab switches', () => {
        const started = cy.stub().as('videosStarted');
        let release!: () => void;
        const gate = new Promise<void>((resolve) => {
            release = resolve;
        });
        cy.intercept('GET', '**/api/tournament/get_videos/participant*', (req) => {
            started();
            return gate.then(() => {
                req.reply({ body: [] });
            });
        }).as('videos');
        setDirectoryPicker(new FakeDirectoryHandle());
        mountTournament();
        cy.get('@videosStarted').should('have.been.calledOnce');
        cy.contains('button', 'Select folder').should('be.disabled');
        cy.then(() => {
            release();
        });
        cy.wait('@videos');
        cy.contains('button', 'Select folder').click();
        cy.contains('.el-dialog button', 'Watch new files only').click();
        cy.contains('Watching videos').should('be.visible');
        cy.get('[data-cy=personal-score-refresh]').should('be.disabled');
        cy.get('#tab-personal').click();
        cy.get('#tab-participants').click();
        cy.contains('Watching videos').should('be.visible');
        cy.get('@showDirectoryPicker').should('have.been.calledOnce');
        cy.contains('button', 'Pause').click();
        cy.get('[data-cy=personal-score-refresh]').should('be.enabled');
    });

    it('keeps finished tournament data accessible and exports only after awards', () => {
        cy.intercept('GET', '**/api/tournament/get_videos/participant*', { body: [] }).as('videos');
        cy.intercept('GET', '**/api/tournament/get_videos/tournament*', { body: [] }).as('allVideos');
        const data = mountTournament();
        cy.wait('@videos');
        cy.then(() => {
            data.tournament.endDate = new Date(globalNow.value.getTime() - 1000);
        });
        cy.get('#tab-personal').should('be.visible');
        cy.contains('Registration').should('not.exist');
        cy.get('.auto-uploader').should('not.be.visible');
        cy.contains('Export all video stats').should('not.exist');
        cy.then(() => {
            data.tournament.state = TournamentState.Awarded;
        });
        cy.get('[data-cy=all-participants-tabs]').should('be.visible');
        cy.contains('button', 'Export all video stats').should('have.length', 1).click();
        cy.wait('@allVideos');
        cy.contains('button', 'Player row').click();
        cy.get('[data-cy=summary-count]').should('be.visible');
        cy.contains('Download videos').should('not.exist');
    });
});
