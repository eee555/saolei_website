import { defineComponent, h, ref } from 'vue';

import BaseColorPicker from './BaseColorPicker.vue';

import i18n from '@/i18n';

describe('<BaseColorPicker />', () => {
    it('uses caller dimensions and forwards accessible attributes without changing transparent colors', () => {
        const label = ref('First color');
        const model = ref('rgba(0,0,0,0)');
        const update = cy.spy().as('update');
        cy.mount(defineComponent({
            expose: [],
            render: () => h(BaseColorPicker, { modelValue: model.value,
                class: 'custom-color',
                style: { width: '200px', height: '30px', borderRadius: '4px' },
                'aria-label': label.value,
                'onUpdate:modelValue': (value: string) => {
                    model.value = value; update(value);
                } }),
        }), { global: { plugins: [i18n] } });
        cy.get('.custom-color').should('have.css', 'width', '200px').and('have.css', 'height', '30px').and('have.css', 'border-radius', '4px');
        cy.get('.base-color-picker').should('have.class', 'base-color-picker--empty');
        cy.get('.base-color-picker__input').should('have.attr', 'aria-label', 'First color').and('have.value', '#000000');
        cy.get('@update').should('not.have.been.called');
        cy.then(() => {
            label.value = 'Second color';
        });
        cy.get('.base-color-picker__input').should('have.attr', 'aria-label', 'Second color');
        cy.get('.base-color-picker__input').invoke('val', '#123456').trigger('input', { force: true });
        cy.get('@update').should('have.been.calledOnceWith', '#123456');
        cy.get('.base-color-picker__swatch').should('have.css', 'background-color', 'rgb(18, 52, 86)');
        cy.get('.base-color-picker__clear').click();
        cy.get('@update').should('have.been.calledWith', 'rgba(0,0,0,0)');
        cy.get('.base-color-picker').should('have.class', 'base-color-picker--empty');
    });

    it('reflects external colors without modifying legacy formats and blocks disabled edits', () => {
        const model = ref('rgba(255, 255, 255, 0)');
        const disabled = ref(false);
        const update = cy.spy().as('update');
        cy.mount(defineComponent({
            expose: [],
            render: () => h(BaseColorPicker, { modelValue: model.value, disabled: disabled.value, style: { width: '160px', height: '24px' }, 'onUpdate:modelValue': update }),
        }), { global: { plugins: [i18n] } });
        cy.get('.base-color-picker').should('have.class', 'base-color-picker--empty');
        cy.get('@update').should('not.have.been.called');
        cy.then(() => {
            model.value = '#abcdef'; disabled.value = true;
        });
        cy.get('.base-color-picker__input').should('have.value', '#abcdef').and('be.disabled').invoke('val', '#123456').trigger('input', { force: true });
        cy.get('.base-color-picker__clear').should('be.disabled').trigger('click', { force: true });
        cy.get('@update').should('not.have.been.called');
    });
});
