/* eslint-disable vue/one-component-per-file */
import { defineComponent, h } from 'vue';
import type { Component, PropType } from 'vue';

import AllParticipants from './AllParticipants.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { pinia } from '@/store/create';
import { TournamentState, TournamentSubclass } from '@/utils/ms_const';
import { Tournament } from '@/utils/tournaments';
import type { VideoAbstract } from '@/utils/videoabstract';

interface TestParticipant {
    id: number;
    user_id: number | null;
    name: string;
}

const participants: TestParticipant[] = [
    { id: 11, user_id: 101, name: 'Alpha' },
    { id: 22, user_id: 202, name: 'Bravo' },
    { id: 33, user_id: null, name: 'Anonymous' },
    { id: 44, user_id: 0, name: 'Zero' },
];

const TypedAllParticipants = AllParticipants as unknown as Component;

interface AllSummarySlotProps {
    data: TestParticipant[];
    onParticipantSelect: (participant: TestParticipant) => void;
}

interface PersonalSummarySlotProps {
    videos: VideoAbstract[];
}

const TestHost = defineComponent({
    components: { AllParticipants: TypedAllParticipants },
    props: {
        result: {
            type: Array as PropType<TestParticipant[]>,
            required: true,
        },
    },
    expose: [],
    setup() {
        const tournament = new Tournament({
            id: 9001,
            name: 'Tab Test Tournament',
            subclass: TournamentSubclass.GSC,
            state: TournamentState.Awarded,
            data: { order: 1, token: 'G00001' },
        });
        return { tournament };
    },
    render() {
        return h(TypedAllParticipants, {
            tournament: this.tournament,
            result: this.result,
        }, {
            allSummary: ({ data, onParticipantSelect }: AllSummarySlotProps) => h('div', {}, data.map((participant) => h('button', {
                key: participant.id,
                'data-cy': `participant-${participant.id}`,
                onClick: () => {
                    onParticipantSelect(participant);
                },
            }, participant.name))),
            personalSummary: ({ videos }: PersonalSummarySlotProps) => h('div', { 'data-cy': 'personal-summary' }, `videos: ${videos.length}`),
        });
    },
});

const PlayerNameStub = defineComponent({
    props: { userId: { type: Number, required: true } },
    expose: [],
    render() {
        return h('span', { 'data-cy': 'player-name' }, `User ${this.userId}`);
    },
});

const PersonalViewStub = defineComponent({
    props: {
        userId: { type: Number, required: true },
        tournamentId: { type: Number, required: true },
    },
    expose: [],
    render() {
        return h('section', { 'data-cy': 'personal-view' }, this.$slots.personalSummary?.({ videos: [] }));
    },
});

function mountAllParticipants(options: {
    result?: TestParticipant[];
} = {}) {
    i18n.global.locale.value = 'en';
    cy.mount(TestHost as never, {
        props: {
            result: options.result ?? participants,
        },
        global: {
            plugins: [pinia, i18n],
            config: { globalProperties: { $axios } },
            stubs: {
                PersonalView: PersonalViewStub,
                PlayerName: PlayerNameStub,
            },
        },
    } as never);
}

function topLevelTabItems() {
    return cy.get('[data-cy=all-participants-tabs] > .el-tabs__header .el-tabs__item');
}

function topLevelTab(id: number) {
    return cy.get(`[id="tab-${id}"]`);
}

function activeTopLevelTabShouldBe(id: number) {
    cy.get('.el-tabs__item.is-active').should('have.attr', 'id', `tab-${id}`);
}

describe('<AllParticipants />', () => {
    it('opens participant tabs and reuses an existing tab', () => {
        mountAllParticipants();

        topLevelTabItems().should('have.length', 1);
        cy.get('[data-cy=participant-11]').click();
        topLevelTabItems().should('have.length', 2);
        activeTopLevelTabShouldBe(11);
        cy.get('[data-cy=personal-summary]').should('contain.text', 'videos: 0');

        topLevelTabItems().first().click();
        cy.get('[data-cy=participant-22]').click();
        topLevelTabItems().should('have.length', 3);
        activeTopLevelTabShouldBe(22);

        topLevelTabItems().first().click();
        cy.get('[data-cy=participant-11]').click();
        topLevelTabItems().should('have.length', 3);
        activeTopLevelTabShouldBe(11);
    });

    it('keeps the active participant tab when another tab is closed', () => {
        mountAllParticipants();

        cy.get('[data-cy=participant-11]').click();
        topLevelTabItems().first().click();
        cy.get('[data-cy=participant-22]').click();
        activeTopLevelTabShouldBe(22);

        topLevelTab(11).find('[data-cy=all-participants-tab-close]').click();
        topLevelTabItems().should('have.length', 2);
        topLevelTab(11).should('not.exist');
        activeTopLevelTabShouldBe(22);

        topLevelTab(22).find('[data-cy=all-participants-tab-close]').click();
        topLevelTabItems().should('have.length', 1);
        activeTopLevelTabShouldBe(-1);
        cy.get('[data-cy=personal-view]').should('not.exist');
    });

    it('does not open tabs for invalid participants', () => {
        mountAllParticipants();

        cy.get('[data-cy=participant-33]').click();
        topLevelTabItems().should('have.length', 1);
        cy.get('[data-cy=participant-44]').click();
        topLevelTabItems().should('have.length', 1);

        cy.get('[data-cy=participant-11]').click();
        topLevelTabItems().should('have.length', 2);
        activeTopLevelTabShouldBe(11);
    });
});
