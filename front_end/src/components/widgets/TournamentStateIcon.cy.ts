import TournamentStateIcon from './TournamentStateIcon.vue';

import i18n from '@/i18n';
import { TournamentState } from '@/utils/ms_const';

describe('<TournamentStateIcon />', () => {
    it('Pending', () => {
        // see: https://on.cypress.io/mounting-vue
        cy.mount(TournamentStateIcon, {
            props: {
                state: TournamentState.Pending,
            },
            global: {
                plugins: [i18n],
            },
        });
        cy.contains('Pending');
    });

    it('Preparing', () => {
        cy.mount(TournamentStateIcon, {
            props: {
                state: TournamentState.Preparing,
            },
            global: {
                plugins: [i18n],
            },
        });
        cy.contains('Preparing');
    });

    it('Ongoing', () => {
        cy.mount(TournamentStateIcon, {
            props: {
                state: TournamentState.Ongoing,
            },
            global: {
                plugins: [i18n],
            },
        });
        cy.contains('Ongoing');
    });

    it('Finished', () => {
        cy.mount(TournamentStateIcon, {
            props: {
                state: TournamentState.Finished,
            },
            global: {
                plugins: [i18n],
            },
        });
        cy.contains('Finished');
    });

    it('Awarded', () => {
        cy.mount(TournamentStateIcon, {
            props: {
                state: TournamentState.Awarded,
            },
            global: {
                plugins: [i18n],
            },
        });
        cy.contains('Awarded');
    });

    it('Cancelled', () => {
        cy.mount(TournamentStateIcon, {
            props: {
                state: TournamentState.Cancelled,
            },
            global: {
                plugins: [i18n],
            },
        });
        cy.contains('Cancelled');
    });
});
