import { reactive } from 'vue';

import { defaultMouseTraceAppearance } from './mouseTrace';
import MouseTraceSettings from './MouseTraceSettings.vue';

import i18n from '@/i18n';

function editNumber(selector: string, value: string) {
    cy.get(selector).clear();
    cy.get(selector).type(value);
    cy.get(selector).blur();
}

describe('<MouseTraceSettings />', () => {
    it('edits line colors and all marker props, retaining styles while hidden', () => {
        const appearance = reactive(defaultMouseTraceAppearance());
        cy.mount(MouseTraceSettings, { props: { modelValue: appearance }, global: { plugins: [i18n] } });
        editNumber('.mouse-trace-settings__line-width', '0.2');
        for (const state of ['uu', 'du', 'ud', 'dd']) {
            cy.get(`.mouse-trace-settings__color--${state} input`).invoke('val', '#123456').trigger('input');
        }
        cy.get('.mouse-trace-settings__marker--lc summary').click();
        cy.get('.mouse-trace-settings__marker--lc').within(() => {
            cy.get('.mouse-trace-settings__enabled').should('not.be.checked');
            cy.get('.mouse-trace-settings__shape').should('be.disabled');
            cy.get('.mouse-trace-settings__enabled').check();
            cy.get('.mouse-trace-settings__shape').select('square');
            editNumber('.mouse-trace-settings__size', '0.8');
            editNumber('.mouse-trace-settings__stroke-width', '0.12');
            editNumber('.mouse-trace-settings__opacity', '0.4');
            cy.get('.mouse-trace-settings__fill input').invoke('val', '#abcdef').trigger('input');
            cy.get('.mouse-trace-settings__stroke .base-color-picker__clear').click();
            cy.get('.mouse-trace-settings__enabled').uncheck();
            cy.get('.mouse-trace-settings__shape').should('be.disabled');
            cy.get('.mouse-trace-settings__fill input').should('be.disabled');
            cy.get('.mouse-trace-settings__enabled').check();
            cy.get('.mouse-trace-settings__shape').should('have.value', 'square').and('not.be.disabled');
            cy.get('.mouse-trace-settings__size').should('have.value', '0.8');
        });
        cy.wrap(appearance).should((value) => {
            expect(value.lineWidth).to.eq(0.2);
            expect(value.color).to.deep.eq({ uu: '#123456', du: '#123456', ud: '#123456', dd: '#123456' });
            expect(value.markers.lc).to.deep.eq({ enabled: true, shape: 'square', size: 0.8, strokeWidth: 0.12, opacity: 0.4, fill: '#abcdef', stroke: 'rgba(0,0,0,0)' });
        });
        for (const action of ['lr', 'rc', 'rr']) {
            cy.get(`.mouse-trace-settings__marker--${action} summary`).click();
            cy.get(`.mouse-trace-settings__marker--${action} .mouse-trace-settings__enabled`).should('not.be.checked').check();
            cy.get(`.mouse-trace-settings__marker--${action} .mouse-trace-settings__enabled`).uncheck();
        }
        cy.wrap(appearance).should((value) => {
            expect(value.markers.lr.enabled).to.eq(false);
            expect(value.markers.rc.enabled).to.eq(false);
            expect(value.markers.rr.enabled).to.eq(false);
            expect(value.markers.lc.enabled).to.eq(true);
        });
    });
});
