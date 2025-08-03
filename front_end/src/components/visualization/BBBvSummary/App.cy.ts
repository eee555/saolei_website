import BBBvSummary from './App.vue';
import i18n from '@/i18n';
import { pinia } from '@/store/create';
import { VideoAbstract } from '@/utils/videoabstract';

describe('<BBBvSummary />', () => {
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
        cy.mount(BBBvSummary, {
            props: {
                level: 'e',
                videoList: videoList,
            },
            global: {
                plugins: [i18n, pinia],
            },
        });
        cy.get('[data-cy=summary]').contains('Expert 2 Bv in total');
        cy.get('[data-cy=bv-100]').contains('30.000');
        cy.get('[data-cy=bv-155]').then(($el) => {
            const styles = $el[0].style;
            const variables = Array.from(styles).filter((prop) => prop.startsWith('--') && prop.endsWith('fontColor'));
            variables.forEach((varName) => {
                const value = styles.getPropertyValue(varName);
                expect(value).to.equal('#606266');
            });
        });
    });
});
