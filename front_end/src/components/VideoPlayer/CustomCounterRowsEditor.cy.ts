import CustomCounterRowsEditor from './CustomCounterRowsEditor.vue';
import type { CustomCounterConfig } from './types';

const labelInputSelector = '.custom-counter-rows-editor__label input';
const expressionInputSelector = '.custom-counter-rows-editor__expression textarea';

function mountRowsEditor(config: CustomCounterConfig = [
    ['time', 'rtime'],
    ['bvs', 'bbbv_s || "/" || bbbv'],
]) {
    cy.mount(CustomCounterRowsEditor, {
        props: {
            modelValue: config,
        },
    });
}

function setLabel(index: number, value: string) {
    cy.get(labelInputSelector).eq(index).then(($input) => {
        const input = $input[0] as HTMLInputElement;
        input.value = value;
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
    });
}

function setExpression(index: number, value: string) {
    cy.get(expressionInputSelector).eq(index).then(($textarea) => {
        const textarea = $textarea[0] as HTMLTextAreaElement;
        textarea.value = value;
        textarea.dispatchEvent(new Event('input', { bubbles: true }));
        textarea.dispatchEvent(new Event('change', { bubbles: true }));
    });
}

function expectLastModelUpdate(expected: CustomCounterConfig) {
    cy.get('@vue').then((wrapper: ComponentWrapper<typeof CustomCounterRowsEditor>) => {
        const events = wrapper.emitted('update:modelValue') ?? [];
        expect(events.at(-1)).to.deep.equal([expected]);
    });
}

describe('<CustomCounterRowsEditor />', () => {
    it('renders existing rows plus one blank add row', () => {
        mountRowsEditor();

        cy.get('.custom-counter-rows-editor__row').should('have.length', 3);
        cy.get(labelInputSelector).eq(0).should('have.value', 'time');
        cy.get(labelInputSelector).eq(1).should('have.value', 'bvs');
        cy.get(labelInputSelector).eq(2).should('have.value', '');
        cy.get('.custom-counter-rows-editor__drag-handle').should('have.length', 2).and('have.class', 'pi-ellipsis-v');
    });

    it('emits row label and expression edits', () => {
        mountRowsEditor();

        setLabel(0, 'duration');
        expectLastModelUpdate([
            ['duration', 'rtime'],
            ['bvs', 'bbbv_s || "/" || bbbv'],
        ]);

        setExpression(1, 'roundTo(bbbv_s, 3)');
        expectLastModelUpdate([
            ['duration', 'rtime'],
            ['bvs', 'roundTo(bbbv_s, 3)'],
        ]);
    });

    it('adds a row through the blank row at the bottom', () => {
        mountRowsEditor([['time', 'rtime']]);

        setExpression(1, 'left + right');
        setLabel(1, 'clicks');

        expectLastModelUpdate([
            ['time', 'rtime'],
            ['clicks', 'left + right'],
        ]);
        cy.get(labelInputSelector).last().should('have.value', '');
    });

    it('deletes a row when its label is cleared and committed', () => {
        mountRowsEditor([
            ['time', 'rtime'],
            ['bvs', 'bbbv'],
        ]);

        setLabel(0, '');

        expectLastModelUpdate([['bvs', 'bbbv']]);
        cy.get(labelInputSelector).first().should('have.value', 'bvs');
    });
});
