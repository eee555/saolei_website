import ClassicSummary from './Classic.vue';

import i18n from '@/i18n';
import { MS_Mode } from '@/utils/ms_const';
import type { MS_Mode as MSMode } from '@/utils/ms_const';
import { VideoAbstract } from '@/utils/videoabstract';

function video(level: 'i' | 'e', mode: MSMode, timems: number, right_ce = 1): VideoAbstract {
    return new VideoAbstract({
        id: timems,
        upload_time: '2026-01-01T00:00:00Z',
        level,
        mode,
        timems,
        right_ce,
        bv: 100,
        software: 'e',
    });
}

function mountClassicSummary(videos: VideoAbstract[]) {
    cy.mount(ClassicSummary, {
        props: {
            videos,
        },
        global: {
            plugins: [i18n],
        },
    });
}

function cellTexts(index: number) {
    return cy.get('.cell-list').eq(index).find('.cell').then(($cells) => {
        return Array.from($cells).map((cell) => cell.textContent?.replace(/\s+/g, ' ').trim() ?? '');
    });
}

describe('<WeeklyPersonalSummary Classic />', () => {
    it('uses the fastest standard videos, including no-flag play, for classic scoring', () => {
        mountClassicSummary([
            video('i', MS_Mode.SpeedNG, 9876),
            video('i', MS_Mode.Standard, 20000),
            video('i', MS_Mode.Standard, 21000, 0),
            video('i', MS_Mode.Standard, 22000),
            video('i', MS_Mode.Standard, 23000, 0),
            video('i', MS_Mode.Standard, 24000),
            video('i', MS_Mode.Standard, 25000, 0),
            video('e', MS_Mode.SpeedNG, 9876),
            video('e', MS_Mode.Standard, 110000),
            video('e', MS_Mode.Standard, 120000, 0),
            video('e', MS_Mode.Standard, 130000),
        ]);

        cy.get('body').should('contain.text', 'Sum: 340.000');
        cy.get('body').should('contain.text', 'Expert: 230.000');
        cy.get('body').should('contain.text', 'Intermediate: 110.000');
        cy.get('.cell-list').should('have.length', 2);
        cellTexts(0).should('deep.equal', ['110.000', '120.000']);
        cellTexts(1).should('deep.equal', ['20.000', '21.000', '22.000', '23.000', '24.000']);
        cy.get('body').should('not.contain.text', '9.876').and('not.contain.text', '25.000').and('not.contain.text', '130.000');
    });

    it('fills missing scores with the weekly default times', () => {
        mountClassicSummary([
            video('i', MS_Mode.Standard, 20000),
            video('e', MS_Mode.Standard, 110000, 0),
        ]);

        cy.get('body').should('contain.text', 'Sum: 610.000');
        cy.get('body').should('contain.text', 'Expert: 350.000');
        cy.get('body').should('contain.text', 'Intermediate: 260.000');
        cellTexts(0).should('deep.equal', ['110.000', '240']);
        cellTexts(1).should('deep.equal', ['20.000', '60', '60', '60', '60']);
    });
});
