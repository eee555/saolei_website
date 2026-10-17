import { defineComponent, h, ref } from 'vue';

import BoardLayerControl from './BoardLayerControl.vue';

import i18n from '@/i18n';

function mountControl() {
    const visible = ref(true);
    const opacity = ref(1);
    cy.viewport(400, 300);
    cy.mount(defineComponent({
        expose: [],
        render: () => h('div', { class: 'layer-control-test-container', style: { display: 'flex', justifyContent: 'flex-end', height: '120px', overflow: 'hidden' } }, [
            h(BoardLayerControl, { label: 'Probability',
                modelValue: visible.value,
                opacity: opacity.value,
                'onUpdate:opacity': (value: number) => {
                    opacity.value = value;
                },
                'onUpdate:modelValue': (value: boolean) => {
                    visible.value = value;
                } }, {
                toggle: () => h('button', { class: 'base-button layer-control-test-toggle',
                    style: { width: '28px', height: '28px' },
                    onClick: () => {
                        visible.value = !visible.value;
                    } }, '%'),
                settings: () => h('div', { class: 'layer-control-test-section', style: { height: '360px', overflow: 'auto' } }, [
                    h('textarea', { class: 'layer-control-test-setting', style: { height: '320px' }, 'aria-label': 'Layer setting' }),
                ]),
            }),
        ]),
    }), { global: { plugins: [i18n] } });
    cy.wrap(visible).as('visible');
    cy.wrap(opacity).as('opacity');
}

describe('<BoardLayerControl />', () => {
    it('places a separate handle next to the toggle and opens interactive settings to the left', () => {
        mountControl();
        cy.get('.board-settings-control__settings:visible').should('not.exist');
        cy.get('.board-settings-control').should(($control) => {
            expect($control[0].getBoundingClientRect().width).to.eq(40);
        });
        cy.get('.board-settings-control__handle').should('have.attr', 'aria-expanded', 'false').and(($handle) => {
            const handle = $handle[0].getBoundingClientRect();
            const toggle = $handle[0].closest('.board-layer-control')?.querySelector('.layer-control-test-toggle')?.getBoundingClientRect();
            expect(handle.right).to.eq(toggle?.left);
            expect(handle.top).to.eq(toggle?.top);
            expect(handle.bottom).to.eq(toggle?.bottom);
        });
        cy.get('.board-settings-control__handle > i').should('have.class', 'pi-ellipsis-v');
        cy.get('.board-settings-control__handle').click();
        cy.get('@visible').its('value').should('eq', true);
        cy.get('.board-settings-control__handle').should('have.attr', 'aria-expanded', 'true');
        cy.get('.board-settings-control__settings').should('be.visible').and(($settings) => {
            const bounds = $settings[0].getBoundingClientRect();
            const handle = $settings[0].ownerDocument.querySelector('.board-settings-control__handle')?.getBoundingClientRect();
            expect(bounds.right).to.be.at.most(handle?.left ?? 0);
            expect(bounds.left).to.be.at.least(0);
            expect(bounds.top).to.be.at.least(0);
            expect(bounds.bottom).to.be.at.most(300);
            expect($settings[0].closest('[data-tippy-root]')?.parentElement).to.eq($settings[0].ownerDocument.body);
            expect($settings[0].scrollHeight).to.be.greaterThan($settings[0].clientHeight);
        });
        cy.get('.layer-control-test-section').should(($section) => {
            expect($section[0].getBoundingClientRect().height).to.eq(360);
        });
        cy.get('.board-layer-control__opacity-setting').should(($row) => {
            const row = $row[0].getBoundingClientRect();
            const section = $row[0].ownerDocument.querySelector('.layer-control-test-section')?.getBoundingClientRect();
            expect(row.bottom).to.be.at.most(section?.top ?? 0);
        });
        cy.get('.board-layer-control__visible').uncheck();
        cy.get('@visible').its('value').should('eq', false);
        cy.get('.board-settings-control__settings').should('be.visible');
        cy.get('.layer-control-test-setting').type('custom setting');
        cy.get('.board-settings-control__settings').should('be.visible');
        cy.get('.board-settings-control__handle').click();
        cy.get('.board-settings-control__handle').should('have.attr', 'aria-expanded', 'false');
        cy.get('.board-settings-control__settings:visible').should('not.exist');
        cy.get('.board-settings-control').should(($control) => {
            expect($control[0].getBoundingClientRect().width).to.eq(40);
        });
    });

    it('opens with the keyboard and closes with Escape, returning focus to the handle', () => {
        mountControl();
        cy.get('.board-settings-control__handle').focus();
        cy.realPress('Enter');
        cy.get('.board-layer-control__visible').should('be.focused');
        cy.get('.board-layer-control__visible').trigger('keydown', { key: 'Escape' });
        cy.get('.board-settings-control__handle').should('have.attr', 'aria-expanded', 'false').and('be.focused');
        cy.get('@visible').its('value').should('eq', true);
    });

    it('updates numeric opacity independently of visibility and preserves it when settings reopen', () => {
        mountControl();
        cy.get('.board-settings-control__handle').click();
        cy.get('.board-layer-control__opacity').should('have.value', '1').and('have.attr', 'min', '0').and('have.attr', 'max', '1');
        cy.get('.board-layer-control__opacity-setting > output').should('have.text', '100%');
        for (const value of [0, 0.35, 1]) {
            cy.get('.board-layer-control__opacity').invoke('val', value).trigger('input');
            cy.get('@opacity').its('value').should('eq', value);
            cy.get('.board-layer-control__opacity-setting > output').should('have.text', `${Math.round(value * 100)}%`);
            cy.get('@visible').its('value').should('eq', true);
            cy.get('.board-settings-control__settings').should('be.visible');
        }
        cy.get('.board-layer-control__opacity').invoke('val', 0.35).trigger('input');
        cy.get('.board-layer-control__visible').uncheck();
        cy.get('.board-layer-control__visible').check();
        cy.get('.board-settings-control__handle').click();
        cy.get('.board-settings-control__handle').click();
        cy.get('.board-layer-control__opacity').should('have.value', '0.35');
        cy.get('@opacity').its('value').should('eq', 0.35);
    });

    it('closes on an outside click without changing visibility', () => {
        mountControl();
        cy.get('.board-settings-control__handle').click();
        cy.get('.board-settings-control__settings').should('be.visible');
        cy.get('.layer-control-test-container').click('topRight');
        cy.get('.board-settings-control__handle').should('have.attr', 'aria-expanded', 'false');
        cy.get('.board-settings-control__settings:visible').should('not.exist');
        cy.get('@visible').its('value').should('eq', true);
    });
});
