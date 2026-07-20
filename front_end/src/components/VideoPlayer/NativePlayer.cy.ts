import PrimeVue from 'primevue/config';

import NativePlayer from './NativePlayer.vue';
import { customCounterConfig } from './store';
import { cloneCustomCounterTable, defaultCustomCounterTable } from './types';

import { binaryStringToUint8Array } from '@/../cypress/support/stupidCypress';
import i18n from '@/i18n';
import { videoPlayerConfig } from '@/store';

const fixture = {
    filename: 'c_10_129.073_24_0.186_Pu Tian Yi(Hu Bei).evf',
    src: '/video/preview/?id=c_10_129.073_24_0.186_Pu%20Tian%20Yi%28Hu%20Bei%29.evf',
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
        const responseBody = data.buffer.slice(data.byteOffset, data.byteOffset + data.byteLength);
        cy.intercept('GET', '**/video/preview/**', (request) => {
            expect(request.url).to.contain('/video/preview/');
            request.reply({
                statusCode: 200,
                headers: { 'content-type': 'application/octet-stream' },
                body: responseBody,
            });
        }).as('getVideo');
    });
}

function dynamicParamCell(label: string, options?: Partial<Cypress.Timeoutable>) {
    return cy.contains('.custom-counter-wrap th', new RegExp(`^${label}$`), options).parents('tr').find('td');
}

function waitForLoadedPlayer() {
    cy.get('.native-player', { timeout: 10000 }).should(($player) => {
        expect($player.find('.native-player__content'), $player.text()).to.have.length(1);
    });
}

describe('<NativePlayer />', () => {
    beforeEach(() => {
        cy.clearLocalStorage('custom-counter-config');
        cy.clearLocalStorage('video-player-config');
        customCounterConfig.value = {
            table: cloneCustomCounterTable(defaultCustomCounterTable),
            thWidth: 90,
            tdWidth: 130,
            fontSize: 12,
        };
        videoPlayerConfig.value = {
            backend: 'native',
            cellSize: 16,
            strangeDustTrust: false,
        };
    });

    it('loads and renders an EVF replay from fixtures', () => {
        mockVideoFixture();
        cy.mount(NativePlayer, mountOptions(fixture.src));

        cy.wait('@getVideo');
        waitForLoadedPlayer();
        cy.get('.native-player__content').should('be.visible');
        cy.get('.player-main').should('be.visible');
        cy.get('.custom-counter-wrap').should('exist').and('contain', 'cl');
        dynamicParamCell('bvs').should('contain', '/24');
        cy.get('.custom-counter-wrap').should('contain', 'time');
        cy.get('.custom-counter-wrap').should('contain', 'mov');
    });

    it('advances the replay when playing', () => {
        mockVideoFixture();
        cy.mount(NativePlayer, mountOptions(fixture.src));

        cy.wait('@getVideo');
        waitForLoadedPlayer();
        cy.get('.progress-bar__play').click();
        dynamicParamCell('time').should(($time) => {
            expect($time.text()).to.contain('/');
        });
        dynamicParamCell('bvs').should(($bvs) => {
            const match = (/^(\d+)\/(\d+)~/).exec($bvs.text());
            expect(match, $bvs.text()).not.to.equal(null);
            if (match === null) return;
            expect(Number(match[1])).to.be.lessThan(Number(match[2]));
        });
    });

    it('reports fetch response errors from the backend', () => {
        cy.intercept('GET', '**/videos/**', {
            statusCode: 404,
            statusMessage: 'Not Found',
            body: '',
        }).as('getVideo');
        cy.mount(NativePlayer, mountOptions('/videos/'));

        cy.wait('@getVideo');
        cy.get('.native-player').should('contain', '404');
    });
});
