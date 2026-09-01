import PersonalSummary from './PersonalSummary.vue';

import { MS_Mode } from '@/utils/ms_const';
import type { MS_Mode as MSMode } from '@/utils/ms_const';
import { VideoAbstract } from '@/utils/videoabstract';
import { WeeklyTournamentFormat } from '@/utils/weekly';
import type { WeeklyTournamentFormat as WeeklyTournamentFormatValue } from '@/utils/weekly';

function video(level: 'i' | 'e', mode: MSMode, timems: number): VideoAbstract {
    return new VideoAbstract({
        id: timems,
        upload_time: '2026-01-01T00:00:00+08:00',
        level,
        mode,
        timems,
        bv: 100,
        software: 'e',
    });
}

function mountPersonalSummary(tournamentFormat: WeeklyTournamentFormatValue | undefined, videos: VideoAbstract[]) {
    cy.mount(PersonalSummary, {
        props: {
            tournamentFormat,
            videos,
        },
        global: {
            stubs: {
                ClassicSummary: {
                    props: {
                        videos: { type: Array, default: () => [] },
                    },
                    template: '<div data-cy="classic-summary">Classic summary: {{ videos.length }}</div>',
                },
            },
        },
    });
}

describe('<Weekly PersonalSummary />', () => {
    it('renders the classic summary for the classic format', () => {
        mountPersonalSummary(WeeklyTournamentFormat.Classic, [
            video('i', MS_Mode.Standard, 20000),
            video('e', MS_Mode.NoFlag, 110000),
        ]);

        cy.get('[data-cy=classic-summary]').should('have.text', 'Classic summary: 2');
    });

    it('does not render the classic summary for other formats', () => {
        mountPersonalSummary(undefined, [
            video('i', MS_Mode.SpeedNG, 9876),
        ]);

        cy.get('[data-cy=classic-summary]').should('not.exist');
    });
});
