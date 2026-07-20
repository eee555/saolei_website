import CustomCounterSettings from './CustomCounterSettings.vue';
import { cloneCustomCounterTable } from './types';
import type { CustomCounterConfig, CustomCounterTableRow } from './types';

import i18n from '@/i18n';

function createSettings(table: CustomCounterTableRow[] = [['time', 'rtime']]): CustomCounterConfig {
    return {
        table: cloneCustomCounterTable(table),
        thWidth: 90,
        tdWidth: 130,
        fontSize: 12,
    };
}

function mountSettings(settings: CustomCounterConfig = createSettings()) {
    cy.mount(CustomCounterSettings, {
        props: {
            modelValue: settings,
        },
        global: {
            plugins: [i18n],
        },
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

describe('<CustomCounterSettings />', () => {
    it('starts in row editor mode and switches to JSON editor mode', () => {
        mountSettings();

        cy.get('.custom-counter-settings').should('be.visible');
        cy.get('.custom-counter-settings__toolbar .custom-counter-settings__number-setting').should('have.length', 2);
        cy.get('.custom-counter-settings__toolbar .base-input-number').should('have.length', 3);
        cy.get('.custom-counter-rows-editor').should('be.visible');
        cy.get('.custom-counter-json-editor').should('not.exist');

        cy.get('.custom-counter-settings__toolbar .el-checkbox').click();

        cy.get('.custom-counter-rows-editor').should('not.exist');
        cy.get('.custom-counter-json-editor').should('be.visible');
    });

    it('updates table rows from child editors', () => {
        const settings = createSettings();
        mountSettings(settings);

        setInputValue('.custom-counter-rows-editor__label input:first', 'duration');
        cy.then(() => {
            expect(settings.table).to.deep.equal([['duration', 'rtime']]);
        });

        cy.get('.custom-counter-settings__toolbar .el-checkbox').click();
        setInputValue('.custom-counter-json-editor__input textarea', '[["time","etime"]]');
        cy.then(() => {
            expect(settings.table).to.deep.equal([['time', 'etime']]);
        });
    });

    it('updates counter layout settings from the toolbar', () => {
        const settings = createSettings();
        mountSettings(settings);

        setInputValue('.custom-counter-settings__toolbar .base-input-number:first', '95');

        cy.then(() => {
            expect(settings.thWidth).to.equal(95);
        });
    });
});
