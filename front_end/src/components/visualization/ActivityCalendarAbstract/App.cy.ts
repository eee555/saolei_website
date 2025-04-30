import { VideoAbstract } from '@/utils/videoabstract';
import ActivityCalendarAbstract from './App.vue';
import i18n from '@/i18n';

describe('<ActivityCalendarAbstract />', () => {
    before(() => {
        cy.fixture('videoAbstractList.json').then((data) => {
            cy.log(data.data);
            Cypress.env('videoList', data.data.map((video) => new VideoAbstract(video)));
        });
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
    });
});
