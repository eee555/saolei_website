import CustomCounterJsonEditor from './CustomCounterJsonEditor.vue';
import type { CustomCounterConfig } from './types';

const textareaSelector = '.custom-counter-json-editor__input textarea';

function mountJsonEditor(config: CustomCounterConfig = [['time', 'rtime']]) {
    cy.mount(CustomCounterJsonEditor, {
        props: {
            modelValue: config,
        },
    });
}

function setJson(value: string) {
    cy.get(textareaSelector).then(($textarea) => {
        const textarea = $textarea[0] as HTMLTextAreaElement;
        textarea.value = value;
        textarea.dispatchEvent(new Event('input', { bubbles: true }));
        textarea.dispatchEvent(new Event('change', { bubbles: true }));
    });
}

function expectLastModelUpdate(expected: CustomCounterConfig) {
    cy.get('@vue').then((wrapper: ComponentWrapper<typeof CustomCounterJsonEditor>) => {
        const events = wrapper.emitted('update:modelValue') ?? [];
        expect(events.at(-1)).to.deep.equal([expected]);
    });
}

describe('<CustomCounterJsonEditor />', () => {
    it('formats the current config into the textarea', () => {
        mountJsonEditor([
            ['time', 'roundTo(rtime, 3)'],
            ['bvs', 'bbbv_s || "/" || bbbv'],
        ]);

        cy.get(textareaSelector).should('contain.value', '["time","roundTo(rtime, 3)"]');
        cy.get(textareaSelector).should('contain.value', '["bvs","bbbv_s || \\"/\\" || bbbv"]');
    });

    it('emits valid JSON config changes', () => {
        mountJsonEditor();

        setJson('[["time","etime"],["bvs","bbbv"]]');

        expectLastModelUpdate([
            ['time', 'etime'],
            ['bvs', 'bbbv'],
        ]);
        cy.get('.custom-counter-json-editor__error').should('not.exist');
    });

    it('keeps invalid JSON text and shows the parse error', () => {
        mountJsonEditor();

        setJson('[,["time","rtime"]]');

        cy.get(textareaSelector).should('have.value', '[,["time","rtime"]]');
        cy.get('.custom-counter-json-editor__error').should('contain', 'JSON 解析失败');
        cy.get('@vue').then((wrapper: ComponentWrapper<typeof CustomCounterJsonEditor>) => {
            expect(wrapper.emitted('update:modelValue')).to.equal(undefined);
        });
    });

    it('keeps invalid shapes and shows the schema error', () => {
        mountJsonEditor();

        setJson('{"time":"rtime"}');

        cy.get(textareaSelector).should('have.value', '{"time":"rtime"}');
        cy.get('.custom-counter-json-editor__error').should('contain', '二维字符串数组');
        cy.get('@vue').then((wrapper: ComponentWrapper<typeof CustomCounterJsonEditor>) => {
            expect(wrapper.emitted('update:modelValue')).to.equal(undefined);
        });
    });
});
