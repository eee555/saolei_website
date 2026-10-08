import { defineComponent, h, ref } from 'vue';

import MultiSelector from './MultiSelector.vue';

describe('<MultiSelector />', () => {
    it('preserves option order, selection order, tag removal and external model changes', () => {
        const selected = ref(['b']);
        const options = ['a', 'b', 'c'] as const;
        cy.mount(defineComponent({
            expose: [],
            render: () => h(MultiSelector, {
                options,
                labels: ['Alpha', 'Beta', 'Gamma'],
                modelValue: selected.value,
                'onUpdate:modelValue': (value: string[]) => {
                    selected.value = value;
                },
            }),
        }));
        cy.get('.checkbox-group label').should(($labels) => {
            expect($labels.toArray().map((label) => label.textContent?.trim())).to.deep.equal(['Alpha', 'Beta', 'Gamma']);
        });
        cy.get('input[value=b]').should('be.checked');
        cy.contains('label', 'Gamma').click();
        cy.get('input[value=a]').focus();
        cy.realPress('Space');
        cy.wrap(selected).its('value').should('deep.equal', ['b', 'c', 'a']);
        cy.contains('.el-tag', 'Beta').find('.el-tag__close').click();
        cy.get('input[value=b]').should('not.be.checked');
        cy.wrap(selected).its('value').should('deep.equal', ['c', 'a']);
        cy.then(() => {
            selected.value = ['c'];
        });
        cy.get('input[value=a]').should('not.be.checked');
        cy.get('input[value=c]').should('be.checked');
        cy.get('.el-tag').should('have.length', 1).and('contain.text', 'Gamma');
    });

    it('uses option values as labels when labels are omitted', () => {
        cy.mount(MultiSelector, { props: { options: ['time', 'bvs'] } });
        cy.contains('label', 'time').click();
        cy.get('input[value=time]').should('be.checked');
        cy.get('.el-tag').should('contain.text', 'time');
    });
});
