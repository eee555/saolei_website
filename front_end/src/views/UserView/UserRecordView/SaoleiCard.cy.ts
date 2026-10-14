import SaoleiCard from './SaoleiCard.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import type { SaoleiPlayerRecord } from '@/services/saoleiRankingService';
import { pinia } from '@/store/create';

const mountOptions = {
    props: { userId: 42 },
    global: {
        plugins: [i18n, pinia],
        config: {
            globalProperties: {
                $axios,
            },
        },
    },
};

describe('<SaoleiCard />', () => {
    beforeEach(() => {
        const record: SaoleiPlayerRecord = {
            player_id: 42,
            bt: 1234,
            bb: 4.567,
            it: null,
            ib: null,
            et: null,
            eb: null,
            sumt: 2001232,
            sumb: 4.567,
            bt_id: 8001,
            bb_id: 8002,
            it_id: null,
            ib_id: null,
            et_id: null,
            eb_id: null,
            ranks: { bt: 2, bb: 3, it: null, ib: null, et: null, eb: null, sumt: 4, sumb: 5 },
        };
        cy.intercept({ method: 'GET', pathname: '/api/speedranking/player/42' }, {
            body: {
                saolei: record,
                saolei_nf: { ...record, bt: 2345, bb: 0, sumt: 2002343, sumb: 0, ranks: { ...record.ranks, bt: 6, bb: null, sumt: 7, sumb: 8 } },
            },
        }).as('saoleiRecords');
    });

    it('loads both speed rankings once and renders scores with ranks', () => {
        cy.mount(SaoleiCard, mountOptions);

        cy.wait('@saoleiRecords').its('request.query').should('deep.equal', {});

        cy.get('.saolei-record-table').extractTableData().should('deep.equal', [
            ['Saolei.wang Rule', 'Beginner', 'Intermediate', 'Expert', 'Sum'],
            ['Time', '1.234(2)', '--(--)', '--(--)', '2001.232(4)'],
            ['Bvs', '4.567(3)', '--(--)', '--(--)', '4.567(5)'],
            ['Time (NF)', '2.345(6)', '--(--)', '--(--)', '2002.343(7)'],
            ['Bvs (NF)', '0.000(--)', '--(--)', '--(--)', '0.000(8)'],
        ]);
        cy.get('.saolei-record-table .clickable').should('have.length', 4);
        cy.get('@saoleiRecords.all').should('have.length', 1);
    });

    it('reloads for another user and keeps all four rows without records', () => {
        cy.mount(SaoleiCard, mountOptions);
        cy.wait('@saoleiRecords');
        cy.get('.saolei-record-table').contains('1.234(2)').should('be.visible');
        const empty: SaoleiPlayerRecord = {
            player_id: 43,
            bt: null,
            bb: null,
            it: null,
            ib: null,
            et: null,
            eb: null,
            sumt: 2999997,
            sumb: 0,
            bt_id: null,
            bb_id: null,
            it_id: null,
            ib_id: null,
            et_id: null,
            eb_id: null,
            ranks: { bt: null, bb: null, it: null, ib: null, et: null, eb: null, sumt: null, sumb: null },
        };
        cy.intercept({ method: 'GET', pathname: '/api/speedranking/player/43' }, {
            body: { saolei: empty, saolei_nf: empty },
        }).as('emptyRecords');
        cy.get<ComponentWrapper<typeof SaoleiCard>>('@vue').then((wrapper) => wrapper.setProps({ userId: 43 }));
        cy.wait('@emptyRecords');
        cy.get('.saolei-record-table tbody').extractTableData().should('deep.equal', [
            ['Time', '--(--)', '--(--)', '--(--)', '2999.997(--)'],
            ['Bvs', '--(--)', '--(--)', '--(--)', '0.000(--)'],
            ['Time (NF)', '--(--)', '--(--)', '--(--)', '2999.997(--)'],
            ['Bvs (NF)', '--(--)', '--(--)', '--(--)', '0.000(--)'],
        ]);
        cy.get('.saolei-record-table .clickable').should('not.exist');
    });
});
