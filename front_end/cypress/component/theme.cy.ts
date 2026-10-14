import '@/styles/link.css';

import { defineComponent, h } from 'vue';

import { getTextColor } from '../../src/utils/colors';

import BaseButton from '@/components/common/BaseButton.vue';
import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import InputNumber from '@/components/common/InputNumber.vue';

const ThemeFixture = defineComponent({
    expose: [],
    render: () => h('div', {
        // Library variables must not control native project components.
        style: {
            '--el-text-color-regular': '#ff00ff',
            '--el-color-primary': '#ff00ff',
            '--el-fill-color-blank': '#ff00ff',
            '--el-border-color': '#ff00ff',
            '--el-font-size-base': '40px',
            '--el-input-text-color': '#ff00ff',
            '--el-table-border-color': '#ff00ff',
        },
    }, [
        h('span', { class: 'text', 'data-cy': 'theme-text' }, 'Text'),
        h('a', { class: 'link text text-primary', href: '#', 'data-cy': 'theme-link' }, 'Link'),
        h(BaseCardNormal, { 'data-cy': 'theme-card' }, () => 'Card'),
        h(BaseButton, { 'data-cy': 'theme-button' }, () => 'Default'),
        h(BaseButton, { type: 'primary', plain: true, 'data-cy': 'theme-plain' }, () => 'Plain'),
        h(BaseButton, { disabled: true, 'data-cy': 'theme-disabled' }, () => 'Disabled'),
        h(InputNumber, { modelValue: 5, 'data-cy': 'theme-input' }),
    ]),
});

describe('Project theme variables', () => {
    let initiallyDark = false;

    beforeEach(() => {
        cy.document().then((doc) => {
            initiallyDark = doc.documentElement.classList.contains('dark');
        });
    });

    afterEach(() => {
        cy.document().then((doc) => {
            doc.documentElement.classList.toggle('dark', initiallyDark);
        });
    });

    it('switches mounted native components between light and dark independently of library variables', () => {
        cy.mount(ThemeFixture);

        for (const theme of [
            { dark: false, text: 'rgb(96, 98, 102)', background: 'rgb(255, 255, 255)', border: 'rgb(220, 223, 230)', plain: 'rgb(236, 245, 255)', disabled: 'rgb(245, 247, 250)', rawText: '#606266' },
            { dark: true, text: 'rgb(207, 211, 220)', background: 'rgb(20, 20, 20)', border: 'rgb(76, 77, 79)', plain: 'rgb(24, 34, 43)', disabled: 'rgb(38, 39, 39)', rawText: '#cfd3dc' },
        ]) {
            cy.document().then((doc) => {
                doc.documentElement.classList.toggle('dark', theme.dark);
                expect(getTextColor().trim()).to.equal(theme.rawText);
            });
            cy.get('[data-cy=theme-text]').should('have.css', 'color', theme.text).and('have.css', 'font-size', '14px');
            cy.get('[data-cy=theme-link]').should('have.css', 'color', 'rgb(64, 158, 255)');
            cy.get('[data-cy=theme-card]').should('have.css', 'background-color', theme.background);
            cy.get('[data-cy=theme-button]').should('have.css', 'color', theme.text).
                and('have.css', 'background-color', theme.background).and('have.css', 'border-radius', '0px');
            cy.get('[data-cy=theme-plain]').should('have.css', 'background-color', theme.plain);
            cy.get('[data-cy=theme-disabled]').should('have.css', 'background-color', theme.disabled);
            cy.get('[data-cy=theme-input]').should('have.css', 'color', theme.text).
                and('have.css', 'background-color', theme.background).and('have.css', 'border-top-color', theme.border);
        }
    });
});
