import { defineComponent, h, ref } from 'vue';

import ColorSchemeSetting from './ColorSchemeSetting.vue';

import i18n from '@/i18n';
import { PiecewiseColorScheme } from '@/utils/colors';
import type { PiecewiseColorSchemeInterface } from '@/utils/colors';

function mountScheme(thresholds = [10, 20], props = {}) {
    const model = ref<PiecewiseColorSchemeInterface>({ thresholds, colors: ['#112233', 'rgba(0,0,0,0)', '#abcdef'].slice(0, thresholds.length + 1) });
    cy.mount(defineComponent({
        expose: [],
        render: () => h('div', { style: { width: '320px' } }, [h(ColorSchemeSetting, { ...props,
            modelValue: model.value,
            'onUpdate:modelValue': (value: PiecewiseColorSchemeInterface) => {
                model.value = value;
            } })]),
    }), { global: { plugins: [i18n] } });
    cy.wrap(model).as('scheme');
    return model;
}

describe('<ColorSchemeSetting />', () => {
    for (const thresholds of [[10, 20], [20, 10]]) {
        it(`renders the actual interval boundaries and horizontal color controls for ${thresholds.join(',')}`, () => {
            mountScheme(thresholds, { min: 0, max: 100 });
            cy.get('.color-scheme-setting__row').should('have.length', 3).eq(1).within(() => {
                cy.get('.color-scheme-setting__lower-comparison').should('have.text', thresholds[0] < thresholds[1] ? '<' : '≤');
                cy.get('.color-scheme-setting__upper-comparison').should('have.text', thresholds[0] < thresholds[1] ? '≤' : '<');
                cy.get('.color-scheme-setting__threshold').eq(0).should('have.value', '10');
                cy.get('.color-scheme-setting__threshold').eq(1).should('have.value', '20');
                cy.get('.color-scheme-setting__threshold + .color-scheme-setting__remove').should('have.length', 2).and('be.visible');
                cy.get('.base-color-picker').should('have.class', 'base-color-picker--empty');
            });
            cy.get('.color-scheme-setting__color').should(($pickers) => {
                for (const picker of $pickers.toArray()) {
                    const bounds = picker.getBoundingClientRect();
                    expect(bounds.height).to.eq(18);
                    expect(bounds.width).to.be.greaterThan(48);
                    expect(bounds.width).to.be.at.most(96);
                    expect(bounds.right).to.be.at.most(picker.closest('.color-scheme-setting')?.getBoundingClientRect().right ?? 0);
                }
            });
            cy.get('.color-scheme-setting__remove').should('have.length', thresholds.length * 2);
            cy.get('.color-scheme-setting__bound').first().should('have.value', '0').and('have.attr', 'readonly');
            cy.get('.color-scheme-setting__bound').last().should('have.value', '100').and('have.attr', 'readonly');
            cy.get('.color-scheme-setting__threshold').should('have.css', 'border-top-width', '0px');
            cy.get('.color-scheme-setting__row').should(($rows) => {
                expect($rows.toArray().map((row) => Array.from(row.querySelectorAll<HTMLInputElement>('.color-scheme-setting__threshold'), (input) => input.value))).to.deep.eq([['0', '10'], ['10', '20'], ['20', '100']]);
            });
            cy.get('.color-scheme-setting').parent().invoke('css', 'width', '800px');
            cy.get('.color-scheme-setting__color').should('have.css', 'width', '96px').and('have.css', 'height', '18px');
            cy.get('.color-scheme-setting__preview').should('not.exist');
            cy.get('.color-scheme-setting__samples').should('not.exist');
            cy.get('.color-scheme-setting > :first-child').should('have.class', 'color-scheme-setting__actions');
        });

        it(`reverses both arrays and switches boundary ownership for ${thresholds.join(',')}`, () => {
            const model = mountScheme(thresholds, { min: 0, max: 100 });
            const initial = { thresholds: [...thresholds], colors: [...model.value.colors] };
            const before = PiecewiseColorScheme.createFromTheme(initial);
            cy.get('.color-scheme-setting__reverse').should('be.enabled').click();
            cy.get('@scheme').its('value').should('deep.equal', { thresholds: [...initial.thresholds].reverse(), colors: [...initial.colors].reverse() });
            cy.get('.color-scheme-setting__row').eq(1).within(() => {
                cy.get('.color-scheme-setting__lower-comparison').should('have.text', thresholds[0] < thresholds[1] ? '≤' : '<');
                cy.get('.color-scheme-setting__upper-comparison').should('have.text', thresholds[0] < thresholds[1] ? '<' : '≤');
                cy.get('.color-scheme-setting__threshold').eq(0).should('have.value', '10');
                cy.get('.color-scheme-setting__threshold').eq(1).should('have.value', '20');
            });
            cy.get('.color-scheme-setting__rows').should(($rows) => {
                expect($rows.find('.color-scheme-setting__row').toArray().map((row) => Array.from(row.querySelectorAll<HTMLInputElement>('.color-scheme-setting__threshold'), (input) => input.value))).to.deep.eq([['0', '10'], ['10', '20'], ['20', '100']]);
                const after = PiecewiseColorScheme.createFromTheme(model.value);
                for (const value of [5, 15, 25]) expect(after.getColor(value)).to.eq(before.getColor(value));
                for (const threshold of thresholds) expect(after.getColor(threshold)).not.to.eq(before.getColor(threshold));
                expect(initial.thresholds).to.deep.eq(thresholds);
            });
            cy.get('.color-scheme-setting__interval-icon > i').first().should('have.class', thresholds[0] < thresholds[1] ? 'pi-circle-fill' : 'pi-circle');
            cy.get('.color-scheme-setting__interval-icon > i').last().should('have.class', thresholds[0] < thresholds[1] ? 'pi-circle' : 'pi-circle-fill');
            cy.get('.color-scheme-setting__reverse').click();
            cy.get('@scheme').its('value').should('deep.equal', initial);
        });

        it(`edits both endpoints and synchronizes shared threshold inputs for ${thresholds.join(',')}`, () => {
            mountScheme(thresholds);
            cy.get('.color-scheme-setting__threshold:not([readonly])').eq(0).invoke('val', '12').trigger('input');
            cy.get('.color-scheme-setting__threshold:not([readonly])').eq(1).should('have.value', '12');
            cy.get('@scheme').its('value.thresholds').should('deep.equal', thresholds[0] < thresholds[1] ? [12, 20] : [20, 12]);
            cy.get('.color-scheme-setting__threshold:not([readonly])').eq(2).invoke('val', '22').trigger('input');
            cy.get('.color-scheme-setting__threshold:not([readonly])').eq(3).should('have.value', '22');
            cy.get('@scheme').its('value.thresholds').should('deep.equal', thresholds[0] < thresholds[1] ? [12, 22] : [22, 12]);
            cy.get('.color-scheme-setting__bound').first().should('have.value', '-∞');
            cy.get('.color-scheme-setting__bound').last().should('have.value', '+∞');
        });
    }

    for (const thresholds of [[], [10], [10, 10]]) {
        it(`disables boundary reversal when thresholds have no direction: ${JSON.stringify(thresholds)}`, () => {
            const model = mountScheme(thresholds);
            const initial = JSON.stringify(model.value);
            cy.get('.color-scheme-setting__reverse').should('be.disabled').and('have.attr', 'title', 'At least two distinct thresholds are required to switch interval boundaries');
            cy.get('.color-scheme-setting__reverse').trigger('click', { force: true });
            cy.get('@scheme').its('value').should((value) => {
                expect(JSON.stringify(value)).to.eq(initial);
            });
        });
    }

    it('keeps invalid threshold drafts without publishing them, then updates a valid draft', () => {
        mountScheme();
        cy.get('.color-scheme-setting__threshold:not([readonly])').eq(0).invoke('val', '').trigger('input');
        cy.get('.color-scheme-setting__threshold:not([readonly])').eq(0).should('have.value', '').and('have.attr', 'aria-invalid', 'true');
        cy.get('.color-scheme-setting__threshold:not([readonly])').eq(1).should('have.value', '');
        cy.get('.color-scheme-setting__error').should('be.visible');
        cy.get('@scheme').its('value.thresholds').should('deep.equal', [10, 20]);
        cy.get('.color-scheme-setting__threshold:not([readonly])').eq(0).invoke('val', '15').trigger('input');
        cy.get('@scheme').its('value.thresholds').should('deep.equal', [15, 20]);
        cy.get('.color-scheme-setting__error').should('not.exist');
        cy.get('.color-scheme-setting__color').first().find('.base-color-picker__clear').click();
        cy.get('@scheme').its('value.colors').should('deep.equal', ['rgba(0,0,0,0)', 'rgba(0,0,0,0)', '#abcdef']);
    });

    it('splits a descending interval and removes its new threshold without changing other colors', () => {
        mountScheme([20, 10], { min: 0, max: 100 });
        cy.get('.color-scheme-setting__split').eq(1).click();
        cy.get('@scheme').its('value').should('deep.equal', { thresholds: [20, 15, 10], colors: ['#112233', 'rgba(0,0,0,0)', 'rgba(0,0,0,0)', '#abcdef'] });
        cy.get('.color-scheme-setting__row').eq(1).find('.color-scheme-setting__remove').last().click();
        cy.get('@scheme').its('value').should('deep.equal', { thresholds: [20, 10], colors: ['#112233', 'rgba(0,0,0,0)', '#abcdef'] });
    });

    it('keeps a failed JSON import and the active configuration, and accepts a corrected descending palette', () => {
        mountScheme([10, 20], { min: 0, max: 100 });
        cy.get('.color-scheme-setting__import-toggle').click();
        cy.get('.color-scheme-setting__json').invoke('val', '[,').trigger('input');
        cy.get('.color-scheme-setting__apply').click();
        cy.get('.color-scheme-setting__json').should('have.value', '[,');
        cy.get('.color-scheme-setting__error').should('contain.text', 'Invalid JSON');
        cy.get('@scheme').its('value.thresholds').should('deep.equal', [10, 20]);
        cy.get('.color-scheme-setting__json').invoke('val', JSON.stringify({ thresholds: [10, 120], colors: ['rgba(0,0,0,0)', '#112233', '#abcdef'] })).trigger('input');
        cy.get('.color-scheme-setting__apply').click();
        cy.get('.color-scheme-setting__error').should('contain.text', 'allowed range');
        const valid = { thresholds: [75, 25], colors: ['rgba(0,0,0,0)', '#123456', '#abcdef'] };
        cy.get('.color-scheme-setting__json').invoke('val', JSON.stringify(valid)).trigger('input');
        cy.get('.color-scheme-setting__apply').click();
        cy.get('@scheme').its('value').should('deep.equal', valid);
        cy.get('.color-scheme-setting__json').should('not.exist');
        cy.get('.color-scheme-setting__row').should('have.length', 3);
    });

    it('copies the configuration including transparent colors and reports a rejected copy without an uncaught error', () => {
        const model = mountScheme();
        cy.window().then((win) => {
            const copy = cy.stub(win.navigator.clipboard, 'writeText').as('copy');
            copy.onFirstCall().resolves();
            copy.onSecondCall().rejects(new Error('Clipboard denied'));
        });
        cy.get('.color-scheme-setting__export').click();
        cy.get('@copy').should('have.been.calledOnceWith', JSON.stringify(model.value, null, 2));
        cy.closeElNotifications();
        cy.get('.color-scheme-setting__export').click();
        cy.get('.el-notification').should('be.visible');
        cy.closeElNotifications();
    });
});
