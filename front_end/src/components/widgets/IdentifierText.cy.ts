import { showInvisibleIdentifiers } from './identifierDisplay';
import IdentifierText from './IdentifierText.vue';

import i18n from '@/i18n';

describe('IdentifierText', () => {
    beforeEach(() => {
        showInvisibleIdentifiers.value = false;
    });

    afterEach(() => {
        showInvisibleIdentifiers.value = false;
        cy.get('html').invoke('removeClass', 'dark');
    });

    it('toggles the display while keeping literal marker characters distinct', () => {
        const text = '␠ \u200B';
        cy.mount(IdentifierText, { props: { text }, global: { plugins: [i18n] } });
        cy.get('.identifier-text').should('have.text', text);
        cy.then(() => {
            showInvisibleIdentifiers.value = true;
        });
        cy.get('.identifier-text').should('have.text', '␠␠⟦U+200B⟧');
        cy.get('.identifier-escape').should('have.length', 2);
        cy.get('.identifier-escape[data-identifier-part="1"]').focus();
        cy.get('.identifier-escape[data-identifier-part="1"]').should('be.focused');
        cy.get('[data-tippy-root]').should('be.visible').and('contain.text', 'U+0020 SPACE');
        cy.get('.identifier-escape[data-identifier-part="1"]').blur();
        cy.shouldBeAbsentOrHidden('[data-tippy-root]');
        cy.get('.identifier-escape[data-identifier-part="2"]').realHover();
        cy.get('[data-tippy-root]').should('be.visible').and('contain.text', 'U+200B ZERO WIDTH SPACE');
        cy.then(() => {
            showInvisibleIdentifiers.value = false;
        });
        cy.get('.identifier-text').should('have.text', text);
        cy.get('.identifier-escape').should('not.exist');
    });

    it('distinguishes escapes in both light and dark themes', () => {
        showInvisibleIdentifiers.value = true;
        cy.mount(IdentifierText, { props: { text: 'a b' }, global: { plugins: [i18n] } });
        for (const dark of [false, true]) {
            cy.get('html').invoke('toggleClass', 'dark', dark);
            cy.get('.identifier-escape').should(($marker) => {
                const root = $marker[0].closest('.identifier-text');
                const view = $marker[0].ownerDocument.defaultView;
                if (!root || !view) throw new Error('Missing identifier root or window');
                expect(view.getComputedStyle($marker[0]).color).not.to.equal(view.getComputedStyle(root).color);
            });
            cy.get('.identifier-escape').should('have.css', 'text-decoration-line', 'underline');
        }
    });

    it('copies original characters when selecting all or part of the escaped identifier', () => {
        showInvisibleIdentifiers.value = true;
        const text = 'ab\u200Bcd';
        cy.mount(IdentifierText, { props: { text }, global: { plugins: [i18n] } });
        cy.get('.identifier-text').then(($text) => {
            const [root] = $text;
            const document = root.ownerDocument;
            const selection = document.getSelection();
            if (!selection) throw new Error('Selection is unavailable');
            const range = document.createRange();
            range.selectNodeContents(root);
            selection.removeAllRanges();
            selection.addRange(range);
            const clipboard = new DataTransfer();
            root.dispatchEvent(new ClipboardEvent('copy', { clipboardData: clipboard, bubbles: true, cancelable: true }));
            expect(clipboard.getData('text/plain')).to.equal(text);
            const first = root.querySelector('[data-identifier-part="0"]')?.firstChild;
            const last = root.querySelector('[data-identifier-part="2"]')?.firstChild;
            if (!first || !last) throw new Error('Missing visible identifier fragments');
            range.setStart(first, 1);
            range.setEnd(last, 1);
            selection.removeAllRanges();
            selection.addRange(range);
            root.dispatchEvent(new ClipboardEvent('copy', { clipboardData: clipboard, bubbles: true, cancelable: true }));
            expect(clipboard.getData('text/plain')).to.equal('b\u200Bc');
            selection.removeAllRanges();
        });
    });
});
