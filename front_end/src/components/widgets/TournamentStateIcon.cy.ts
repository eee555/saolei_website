import TournamentStateIcon from './TournamentStateIcon.vue';
import { TournamentState } from '@/utils/ms_const';
import i18n from '@/i18n';

describe('<TournamentStateIcon />', () => {
    it(TournamentState.Pending, () => {
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

    it(TournamentState.Preparing, () => {
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

    it(TournamentState.Ongoing, () => {
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

    it(TournamentState.Finished, () => {
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

    it(TournamentState.Awarded, () => {
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

    it(TournamentState.Cancelled, () => {
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
