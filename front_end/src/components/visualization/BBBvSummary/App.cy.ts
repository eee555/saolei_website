import BBBvSummary from './App.vue';

import i18n from '@/i18n';
import { BBBvSummaryConfig } from '@/store';
import { pinia } from '@/store/create';
import type { VideoAbstractData } from '@/utils/videoabstract';
import { VideoAbstract } from '@/utils/videoabstract';

describe('<BBBvSummary />', () => {
    beforeEach(() => {
        cy.clearLocalStorage('bbbv-summary-config');
        cy.clock(new Date('2025-12-15T00:00:00Z'));
        cy.fixture<Fixture<VideoAbstractData[]>>('videoAbstractList.json').then((data) => {
            Cypress.expose('videoList', data.data.map((video) => new VideoAbstract(video)));
        });
    });

    const mountSummary = (props: Record<string, unknown> = {}) => {
        const videoList = Cypress.expose('videoList');
        cy.mount(BBBvSummary, {
            props: {
                level: 'e',
                videoList: videoList,
                ...props,
            },
            global: {
                plugins: [i18n, pinia],
            },
        });
    };

    it('renders the optional header, BV range, and grouped expert cells', () => {
        BBBvSummaryConfig.value.showIcon = '';
        mountSummary({ header: true });

        cy.get('[data-cy=summary]').contains('Expert 3 Bv in total');
        cy.contains('100-109').should('be.visible');
        cy.contains('150-159').should('be.visible');

        for (let digit = 0; digit < 10; digit += 1) {
            cy.contains('.text-small', digit.toString()).should('be.visible');
        }

        cy.get('[data-cy=bv-100]').should('contain', '25.000');
        cy.get('[data-cy=bv-101]').should('contain', '45.000');
        cy.get('[data-cy=bv-155]').should('contain', '108.463');
        cy.get('[data-cy=bv-102]').should('exist').and('not.contain', '45.000');
        cy.get('[data-cy=bv-99]').should('not.exist');
        cy.get('[data-cy=bv-160]').should('not.exist');

        cy.get('[data-cy=bv-100]').parent().should('have.css', 'display', 'grid').then(($el) => {
            expect($el.css('grid-template-columns').split(' ').length).to.equal(10);
        });
    });

    it('uses the selected template when deciding what each grouped cell displays', () => {
        BBBvSummaryConfig.value.template = 'ioe';
        BBBvSummaryConfig.value.showIcon = '';
        mountSummary();

        cy.get('[data-cy=bv-100]').should('contain', '1.000');
        cy.get('[data-cy=bv-101]').should('contain', '2.020');
    });

    it('uses custom sort and display settings without rendering header controls', () => {
        BBBvSummaryConfig.value.template = 'custom';
        BBBvSummaryConfig.value.sortBy = 'timems';
        BBBvSummaryConfig.value.sortDesc = true;
        BBBvSummaryConfig.value.displayBy = 'bvs';
        BBBvSummaryConfig.value.showIcon = '';
        mountSummary();

        cy.contains('Find min').should('not.exist');
        cy.get('[data-cy=bv-100]').should('contain', '3.333');
        cy.get('[data-cy=bv-101]').should('contain', '2.244');
    });

    it('supports the path template offered by the header', () => {
        Object.assign(BBBvSummaryConfig.value, { template: 'path', showIcon: '' });
        mountSummary({
            videoList: [
                new VideoAbstract({
                    id: 101,
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
                    path: 64,
                }),
                new VideoAbstract({
                    id: 102,
                    upload_time: '2025-01-15T00:00:00.000Z',
                    end_time: '2025-01-15T00:20:00.000Z',
                    level: 'e',
                    mode: '00',
                    timems: 40000,
                    bv: 100,
                    state: 'c',
                    software: 'e',
                    cl: 200,
                    ce: 100,
                    path: 32,
                }),
            ],
        });

        cy.get('[data-cy=bv-100]').should('contain', '32');
    });

    it('groups by the requested level only', () => {
        BBBvSummaryConfig.value.showIcon = '';
        BBBvSummaryConfig.value.displayBy = 'time';
        mountSummary({ level: 'i' });

        cy.get('[data-cy=summary]').contains('Intermediate 1 Bv in total');
        cy.get('[data-cy=bv-100]').should('contain', '60.000');
        cy.contains('110-119').should('not.exist');
    });
});
