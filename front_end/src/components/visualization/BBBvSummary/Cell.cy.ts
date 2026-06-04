import Cell from './Cell.vue';

import i18n from '@/i18n';
import { pinia } from '@/store/create';
import { PiecewiseColorScheme } from '@/utils/colors';
import { VideoAbstract } from '@/utils/videoabstract';

const makeVideo = (overrides: Record<string, unknown> = {}) => new VideoAbstract({
    id: 1000,
    upload_time: '2025-01-15T00:00:00.000Z',
    end_time: '2025-01-15T00:10:00.000Z',
    level: 'e',
    mode: '00',
    timems: 30000,
    bv: 100,
    state: 'c',
    software: 'e',
    cl: 200,
    ce: 100,
    file_size: 1024,
    ...overrides,
});

const mountCell = (props: Record<string, unknown> = {}) => {
    cy.mount(Cell, {
        props: {
            level: 'e',
            bv: 100,
            videos: [],
            colorTheme: new PiecewiseColorScheme(['#ffffff', '#000000'], [0, 60]),
            softwareFilter: ['e', 'a', 'r', 'm'],
            showIcon: '',
            newThresh: 1,
            ...props,
        },
        global: {
            plugins: [i18n, pinia],
        },
    });
};

describe('<BBBvSummary Cell />', () => {
    beforeEach(() => {
        cy.clock(new Date('2025-12-15T00:00:00Z'));
    });

    it('renders a blank cell when no video can be selected', () => {
        mountCell({
            videos: [makeVideo({ software: 'e', timems: 20000 })],
            softwareFilter: ['a'],
        });

        cy.get('.cell').should('not.contain', '20.000');
        cy.get('.cell').should('have.css', 'background-color', 'rgba(0, 0, 0, 0)');
    });

    it('selects the minimum and maximum stats', () => {
        const videos = [
            makeVideo({ id: 1, timems: 40000, bv: 100 }),
            makeVideo({ id: 2, timems: 25000, bv: 100 }),
        ];

        mountCell({ videos, sortBy: 'timems', sortDesc: false, displayBy: 'time' });
        cy.get('.cell').should('contain', '25.000');

        cy.get('@vue').then((wrapper: any) => {
            wrapper.setProps({ sortDesc: true });
        });
        cy.get('.cell').should('contain', '40.000');
    });

    it('updates when display stat, software filter, and icons change', () => {
        const videos = [
            makeVideo({ id: 1, software: 'e', timems: 50000, bv: 100, cl: 200 }),
            makeVideo({ id: 2, software: 'a', timems: 30000, bv: 100, cl: 50 }),
        ];

        mountCell({
            videos,
            sortBy: 'ioe',
            sortDesc: true,
            displayBy: 'ioe',
            softwareFilter: ['e', 'a'],
            showIcon: 'software',
        });

        cy.get('.cell').should('contain', '2.000');
        cy.get('.cell img').should('exist');

        cy.get('@vue').then((wrapper: any) => {
            wrapper.setProps({ softwareFilter: ['e'], showIcon: 'state' });
        });
        cy.get('.cell').should('contain', '0.500');
        cy.get('.cell .el-icon').should('exist');
        cy.get('.cell img').should('not.exist');
    });

    it('applies color, readable font color, outline, and new-video emphasis', () => {
        mountCell({
            videos: [
                makeVideo({
                    timems: 25000,
                    upload_time: '2025-12-14T12:00:00.000Z',
                }),
            ],
            displayBy: 'time',
            colorTheme: new PiecewiseColorScheme(['#000000'], [0]),
        });

        cy.get('.cell').should('have.class', 'cell-new').and('have.css', 'background-color', 'rgba(0, 0, 0, 0)').and('have.css', 'outline-style', 'solid').and('have.css', 'box-sizing', 'border-box');
        cy.get('.cell .el-link').should('have.css', 'color', 'rgb(255, 255, 255)');
    });
});
