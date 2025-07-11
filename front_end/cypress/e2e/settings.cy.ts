describe('language auto detect', () => {
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
        it(lang, () => {
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
});

describe('dark mode auto detect', () => {
    it('dark mode', () => {
        cy.visit('http://localhost:8080/#/settings', {
            onBeforeLoad: (win) => {
                cy.stub(win, "matchMedia").withArgs("(prefers-color-scheme: dark)").returns({
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
    it('light mode', () => {
        cy.visit('http://localhost:8080/#/settings', {
            onBeforeLoad: (win) => {
                cy.stub(win, "matchMedia").withArgs("(prefers-color-scheme: dark)").returns({
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
