describe('language setting', () => {
    const languages = {
        'zh-CN': '教程',
        'zh-TW': '教程', // fallback to zh-cn
        'en-GB': 'Guides', // fallback to en
        'en-US': 'Guides', // fallback to en
        'de': 'Hilfe',
        'pl': 'poradniki',
        'fr': 'Guides', // fallback to en
    };

    for (const lang in languages) {
        it(`Detect Sys Language: ${lang}`, () => {
            cy.visit('http://localhost:8080/#/settings', {
                onBeforeLoad: (win) => {
                    Object.defineProperty(win.navigator, 'language', {
                        value: lang,
                        configurable: true,
                    });
                },
            });
            cy.contains(languages[lang]);
        });
    }

    it('Change Language', () => {
        cy.visit('http://localhost:8080/#/settings');
        cy.get('[data-cy=languagePicker]').realClick();
        cy.contains('dev').filter(':visible').click();
        cy.contains('menu.guide');
        cy.get('[data-cy=languagePicker]').realClick();
        cy.contains('简体中文').filter(':visible').click();
        cy.contains('教程');
        cy.get('[data-cy=languagePicker]').realClick();
        cy.contains('English').filter(':visible').click();
        cy.contains('Guides');
        cy.get('[data-cy=languagePicker]').realClick();
        cy.contains('Deutsch').filter(':visible').click();
        cy.contains('Hilfe');
        cy.get('[data-cy=languagePicker]').realClick();
        cy.contains('Polski').filter(':visible').click();
        cy.contains('poradniki');
    });
});

describe('Detect Sys Color Theme', () => {
    it('Dark Mode', () => {
        cy.visit('http://localhost:8080/#/settings', {
            onBeforeLoad: (win) => {
                cy.stub(win, 'matchMedia').withArgs('(prefers-color-scheme: dark)').returns({
                    matches: true,
                    addEventListener: () => {},
                    addListener: () => {},
                });
            },
        });
        cy.getLocalStorage('local').then((value) => {
            expect(value.darkmode).to.be.true;
        });
    });
    it('Light Mode', () => {
        cy.visit('http://localhost:8080/#/settings', {
            onBeforeLoad: (win) => {
                cy.stub(win, 'matchMedia').withArgs('(prefers-color-scheme: dark)').returns({
                    matches: false,
                    addEventListener: () => {},
                    addListener: () => {},
                });
            },
        });
        cy.getLocalStorage('local').then((value) => {
            expect(value.darkmode).to.be.false;
        });
    });
});
