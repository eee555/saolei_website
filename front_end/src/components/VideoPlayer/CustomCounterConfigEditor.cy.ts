import CustomCounterConfigEditor from './CustomCounterConfigEditor.vue';
import type { CustomCounterConfig } from './types';

function mountConfigEditor(config: CustomCounterConfig = [['time', 'rtime']]) {
    cy.mount(CustomCounterConfigEditor, {
        props: {
            modelValue: config,
        },
    });
}

function expectLastModelUpdate(expected: CustomCounterConfig) {
    cy.get('@vue').then((wrapper: ComponentWrapper<typeof CustomCounterConfigEditor>) => {
        const events = wrapper.emitted('update:modelValue') ?? [];
        expect(events.at(-1)).to.deep.equal([expected]);
    });
}

function setInputValue(selector: string, value: string) {
    cy.get(selector).then(($input) => {
        const input = $input[0] as HTMLInputElement | HTMLTextAreaElement;
        input.value = value;
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
    });
}

describe('<CustomCounterConfigEditor />', () => {
    it('starts in row editor mode and switches to JSON editor mode', () => {
        mountConfigEditor();

        cy.get('.custom-counter-config-editor').should('be.visible');
        cy.get('.custom-counter-rows-editor').should('be.visible');
        cy.get('.custom-counter-json-editor').should('not.exist');

        cy.get('.custom-counter-config-editor__toolbar .el-checkbox').click();

        cy.get('.custom-counter-rows-editor').should('not.exist');
        cy.get('.custom-counter-json-editor').should('be.visible');
    });

    it('forwards model updates from child editors', () => {
        mountConfigEditor();

        setInputValue('.custom-counter-rows-editor__label input:first', 'duration');
        expectLastModelUpdate([['duration', 'rtime']]);

        cy.get('.custom-counter-config-editor__toolbar .el-checkbox').click();
        setInputValue('.custom-counter-json-editor__input textarea', '[["time","etime"]]');
        expectLastModelUpdate([['time', 'etime']]);
    });
});
