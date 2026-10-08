import type { Component } from 'vue';
import { defineComponent, h, ref } from 'vue';

import MSLevelFilter from './MSLevelFilter.vue';
import SoftwareFilter from './SoftwareFilter.vue';
import VideoStateFilter from './VideoStateFilter.vue';

import i18n from '@/i18n';
import { MS_Levels, MS_Softwares } from '@/utils/ms_const';

const cases: { name: string; component: Component; values: readonly string[] }[] = [
    { name: 'software', component: SoftwareFilter, values: MS_Softwares },
    { name: 'level', component: MSLevelFilter, values: MS_Levels },
    { name: 'state', component: VideoStateFilter, values: ['c', 'd', 'a', 'b'] },
];

describe('checkbox button filters', () => {
    for (const testCase of cases) {
        it(`updates the ${testCase.name} array before emitting one change per activation`, () => {
            const selected = ref<string[]>([...testCase.values]);
            const onChange = cy.spy().as('change');
            cy.mount(defineComponent({
                expose: [],
                render: () => h(testCase.component, {
                    modelValue: selected.value,
                    'onUpdate:modelValue': (value: string[]) => {
                        selected.value = value;
                    },
                    onChange: (value: string[]) => {
                        expect(value).to.deep.equal(selected.value);
                        onChange([...value]);
                    },
                }),
            }), { global: { plugins: [i18n] } });
            cy.get<HTMLInputElement>('input[type=checkbox]').should('have.length', testCase.values.length).and(($inputs) => {
                $inputs.each((index, input) => {
                    expect(input.value).to.equal(testCase.values[index]);
                    expect(input.checked).to.equal(true);
                });
            });
            cy.get('.checkbox-button').first().click();
            cy.get('input[type=checkbox]').first().should('not.be.checked');
            cy.get('@change').should('have.been.calledOnce').and('have.been.calledWithExactly', testCase.values.slice(1));
            cy.get('input[type=checkbox]').first().focus();
            cy.realPress('Space');
            cy.get('input[type=checkbox]').first().should('be.checked');
            cy.get('@change').should('have.been.calledTwice');
            cy.wrap(selected).its('value').should('deep.equal', [...testCase.values.slice(1), testCase.values[0]]);
            cy.then(() => {
                selected.value = [];
            });
            cy.get<HTMLInputElement>('input[type=checkbox]').should(($inputs) => {
                $inputs.each((_index, input) => {
                    expect(input.checked).to.equal(false);
                });
            });
            cy.get('@change').should('have.been.calledTwice');
        });
    }
});
