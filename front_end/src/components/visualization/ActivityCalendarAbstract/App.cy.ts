import ActivityCalendarAbstract from './App.vue';

import i18n from '@/i18n';
import { VideoAbstract } from '@/utils/videoabstract';

describe('<ActivityCalendarAbstract />', () => {
    before(() => {
        cy.fixture('videoAbstractList.json').then((data) => {
            cy.log(data.data);
            Cypress.env('videoList', data.data.map((video: any) => new VideoAbstract(video)));
        });
        cy.clock(new Date('2025-12-15T00:00:00Z'));
    });
    it('renders', () => {
        // see: https://on.cypress.io/mounting-vue
        const videoList = Cypress.env('videoList');
        cy.mount(ActivityCalendarAbstract, {
            props: {
                videoList: videoList,
            },
            global: {
                plugins: [i18n],
            },
        });
        cy.get('[data-cy=count] > :nth-child(1)').should('contain', '2 videos in total');
        cy.get('[data-cy=size] > :nth-child(1)').should('contain', '56574 bytes');

        cy.get('[data-cy=cell-2025-01-15]').should('have.css', 'background-color', 'rgb(0, 0, 51)');
        cy.get('[data-cy=cell-2025-01-16]').should('have.css', 'background-color', 'rgb(0, 0, 51)');

        cy.get('[data-cy=cell-2025-01-15]').realHover();
        cy.get('[id^=tippy-]').should('contain', '1 videos on 2025-01-15');
        cy.get('[class=dot]').should('have.css', 'background-color', 'rgb(0, 0, 255)');
        cy.get('[data-cy=cell-2025-01-14]').realHover();
        cy.get('[id^=tippy-]').should('contain', 'No video on 2025-01-14');
    });
});
