import { h } from 'vue';

import BaseCodeBlock from './BaseCodeBlock.vue';

import { local } from '@/store';

describe('BaseCodeBlock shared theme', () => {
    const originalDarkMode = local.value.darkmode;

    afterEach(() => {
        local.value.darkmode = originalDarkMode;
    });

    it('keeps multiple code blocks in sync across dark-light-dark switches', () => {
        local.value.darkmode = true;
        cy.mount({
            render: () => h('div', [
                h(BaseCodeBlock, { code: '{"name":"first"}', lang: 'json' }),
                h(BaseCodeBlock, { code: '{"name":"second"}', lang: 'json' }),
            ]),
        });

        cy.get('.v-code-block code.hljs').should('have.length', 2);
        cy.get('.v-code-block code.hljs').eq(0).should('contain.text', 'first');
        cy.get('.v-code-block code.hljs').eq(1).should('contain.text', 'second');
        for (const { dark, background, color, stringColor } of [
            { dark: true, background: 'rgb(28, 27, 27)', color: 'rgb(255, 255, 255)', stringColor: 'rgb(181, 189, 104)' },
            { dark: false, background: 'rgb(246, 246, 246)', color: 'rgb(47, 51, 55)', stringColor: 'rgb(84, 121, 13)' },
            { dark: true, background: 'rgb(28, 27, 27)', color: 'rgb(255, 255, 255)', stringColor: 'rgb(181, 189, 104)' },
        ]) {
            cy.then(() => {
                local.value.darkmode = dark;
            });
            cy.get('.v-code-block code.hljs').each(($code) => {
                cy.wrap($code).should('have.css', 'background-color', background).and('have.css', 'color', color);
                cy.wrap($code).find('.hljs-string').should('have.css', 'color', stringColor);
            });
        }
    });

    it('forwards options, slots, and run events', () => {
        cy.mount(BaseCodeBlock, {
            attrs: { code: '{"name":"test"}', lang: 'json', tabs: true, runTab: true, onRun: cy.stub().as('run') },
            slots: { label: () => h('span', 'Code label') },
        });
        cy.contains('.v-code-block--label', 'Code label').should('be.visible');
        cy.contains('.v-code-block--tab', 'Run').click();
        cy.get('@run').should('have.been.calledOnce');
    });
});
