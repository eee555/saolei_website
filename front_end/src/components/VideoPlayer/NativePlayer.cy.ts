import PrimeVue from 'primevue/config';

import NativePlayer from './NativePlayer.vue';
import { customCounterConfig } from './store';
import { cloneCustomCounterConfig, defaultCustomCounterConfig } from './types';

import { binaryStringToUint8Array } from '@/../cypress/support/stupidCypress';
import i18n from '@/i18n';

const fixture = {
    filename: 'c_10_129.073_24_0.186_Pu Tian Yi(Hu Bei).evf',
    src: '/native-player-test.evf',
};

function mountOptions(src: string) {
    return {
        props: { src },
        global: {
            plugins: [i18n, PrimeVue],
        },
    };
}

function mockVideoFixture() {
    cy.fixture(fixture.filename, 'binary').then((fileContent) => {
        const data = binaryStringToUint8Array(fileContent);
        cy.intercept('GET', fixture.src, {
            statusCode: 200,
            headers: { 'content-type': 'application/octet-stream' },
            body: data,
        }).as('fetchVideo');
    });
}

function dynamicParamCell(label: string, options?: Partial<Cypress.Timeoutable>) {
    return cy.contains('.custom-counter-wrap th', new RegExp(`^${label}$`), options).parents('tr').find('td');
}

describe('<NativePlayer />', () => {
    beforeEach(() => {
        cy.clearLocalStorage('custom-counter-config');
        customCounterConfig.value = cloneCustomCounterConfig(defaultCustomCounterConfig);
    });

    it('loads and renders an EVF replay from fixtures', () => {
        mockVideoFixture();
        cy.mount(NativePlayer, mountOptions(fixture.src));

        cy.wait('@fetchVideo');
        cy.get('.native-player__content').should('be.visible');
        cy.get('.native-player__board-frame').should('be.visible');
        cy.get('.custom-counter-wrap').should('be.visible').and('contain', 'cl');
        dynamicParamCell('column').should('have.text', '8');
        dynamicParamCell('row').should('have.text', '8');
        dynamicParamCell('bvs').should('contain', '/24');
        dynamicParamCell('time').should('contain', '/129.073');
        cy.get('.custom-counter-wrap').should('be.visible');
        cy.get('.custom-counter-wrap').should('contain', 'time');
        cy.get('.custom-counter-wrap').should('contain', 'path');
    });

    it('advances the replay when playing', () => {
        mockVideoFixture();
        cy.mount(NativePlayer, mountOptions(fixture.src));

        cy.wait('@fetchVideo');
        cy.get('.progress-bar__play').click();
        dynamicParamCell('time').should(($time) => {
            expect($time.text()).not.to.equal('0/129.073');
        });
        dynamicParamCell('bvs').should(($bvs) => {
            const match = (/@(\d+)\/(\d+)/).exec($bvs.text());
            expect(match, $bvs.text()).not.to.equal(null);
            if (match === null) return;
            expect(Number(match[1])).to.be.lessThan(Number(match[2]));
        });
    });
});
