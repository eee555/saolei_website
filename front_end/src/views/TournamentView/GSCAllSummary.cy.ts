import GSCAllSummary from './GSCAllSummary.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { GSCParticipant } from '@/utils/gsc';

const realnames = {
    18: 'UserNoFinish',
    6: 'UserChampion',
    82: 'UserNoScore',
};

describe('<GSCAllSummary />', () => {
    beforeEach(() => {
        cy.intercept('GET', '/api/userprofile/avatar/**', {
            statusCode: 404,
        });
        cy.intercept(
            {
                method: 'GET',
                pathname: '/api/userprofile/infobulk',
                query: { ids: '6,18,82' },
            },
            {
                body: [
                    { id: 6, realname: realnames[6] },
                    { id: 18, realname: realnames[18] },
                    { id: 82, realname: realnames[82] },
                ],
            },
        ).as('getUserInfo');
    });

    before(() => {
        cy.fixture('gscAllSummary.json').then((data) => {
            cy.log(data.data);
            Cypress.expose('gscParticipantList', data.data.map((value: any) => new GSCParticipant(value)));
        });
    });
    it('renders', () => {
        // see: https://on.cypress.io/mounting-vue
        const participantList = Cypress.expose('gscParticipantList');
        cy.mount(GSCAllSummary as any, {
            props: {
                data: participantList,
            },
            global: {
                plugins: [i18n],
                config: {
                    globalProperties: {
                        $axios,
                    },
                },
            },
        });

        cy.contains('UserChampion');

        cy.get('.el-table__body').extractTableData().should((tableData) => {
            expect(tableData[0]).to.deep.equal([
                'UserChampion',
                '1.430', '1.770', '33.010',
                '8.850', '10.650', '120.410',
                '36.940', '42.460', '204.980',
                '47.220', '54.880', '358.400',
            ]);
            expect(tableData[1]).to.deep.equal([
                'UserNoFinish',
                '1.467', '10.000', '191.467',
                '60.000', '60.000', '720.000',
                '35.279', '240.000', '995.279',
                '96.746', '310.000', '1906.746',
            ]);
            expect(tableData[2]).to.deep.equal([
                'UserNoScore',
                '10.000', '10.000', '200.000',
                '60.000', '60.000', '720.000',
                '240.000', '240.000', '1200.000',
                '310.000', '310.000', '2120.000',
            ]);
        });
    });
});
