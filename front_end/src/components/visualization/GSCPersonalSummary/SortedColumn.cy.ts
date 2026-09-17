import SortedColumn from './SortedColumn.vue';

import i18n from '@/i18n';
import { MS_Mode, MS_State } from '@/utils/ms_const';
import type { MS_Level } from '@/utils/ms_const';
import type { StandardVideoAbstract, VideoAbstractData } from '@/utils/videoabstract';
import { isStandardVideo, VideoAbstract } from '@/utils/videoabstract';

type SortBy = 'time' | 'bvs' | 'stnb';
interface SortedColumnWrapper {
    vm: {
        sumStat: number;
    };
}

function makeVideo(overrides: Partial<VideoAbstractData> = {}): StandardVideoAbstract {
    const video = new VideoAbstract({
        id: 1,
        upload_time: '2026-01-01T00:00:00Z',
        level: 'i',
        mode: MS_Mode.Standard,
        timems: 30000,
        bv: 100,
        state: MS_State.Official,
        software: 'e',
        ...overrides,
    });

    if (!isStandardVideo(video)) throw new Error('SortedColumn tests require standard-level videos');
    return video;
}

function mountSortedColumn(props: {
    videos?: StandardVideoAbstract[];
    level?: MS_Level;
    sortBy?: SortBy;
    count?: number;
} = {}) {
    cy.mount(SortedColumn, {
        props: {
            videos: [],
            level: 'i',
            sortBy: 'time',
            count: 4,
            ...props,
        },
        global: {
            plugins: [i18n],
        },
    });
}

function linkTexts() {
    return cy.get('.cell .el-link').then(($links) => {
        return Array.from($links).map((link) => link.textContent?.replace(/\s+/g, ' ').trim() ?? '');
    });
}

function cellTexts() {
    return cy.get('.cell').then(($cells) => {
        return Array.from($cells).map((cell) => cell.textContent?.replace(/\s+/g, ' ').trim() ?? '');
    });
}

function exposedSumStat() {
    return cy.get('@vue').then((wrapper) => {
        return (wrapper as unknown as SortedColumnWrapper).vm.sumStat;
    });
}

describe('<GSCPersonalSummary SortedColumn />', () => {
    it('sorts time ascending, filters NaN videos, fills defaults, and exposes the sum', () => {
        mountSortedColumn({
            videos: [
                makeVideo({ id: 1, timems: 40000 }),
                makeVideo({ id: 2, timems: 20000 }),
                makeVideo({ id: 3, timems: NaN }),
                makeVideo({ id: 4, timems: 70000 }),
            ],
        });

        cy.get('.cell').should('have.length', 6);
        linkTexts().should('deep.equal', ['20.000', '40.000', '70.000']);
        cellTexts().should('deep.equal', ['Time', '20.000', '40.000', '70.000', '60', '190.00']);
        cy.get('body').should('not.contain.text', 'NaN');

        exposedSumStat().should('equal', 190);
    });

    it('keeps the highest stat values for non-time columns', () => {
        mountSortedColumn({
            level: 'e',
            sortBy: 'bvs',
            count: 2,
            videos: [
                makeVideo({ id: 1, level: 'e', timems: 40000, bv: 80 }),
                makeVideo({ id: 2, level: 'e', timems: 30000, bv: 90 }),
                makeVideo({ id: 3, level: 'e', timems: 100000, bv: 100 }),
            ],
        });

        cy.get('.cell').should('have.length', 4);
        linkTexts().should('deep.equal', ['3.000', '2.000']);
        cellTexts().should('deep.equal', ['Bvs', '3.000', '2.000', '5.000']);

        exposedSumStat().should('equal', 5);
    });
});
