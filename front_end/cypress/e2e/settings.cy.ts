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
                    Object.defineProperty((win as unknown as Window).navigator, 'language', {
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

describe('Color Theme', () => {
    it('Detect Sys Dark Mode', () => {
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
        cy.getLocalStorage('vueuse-color-scheme').then((value) => {
            expect(value).to.eq('auto');
        });
    });
    it('Detect Sys Light Mode', () => {
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
        cy.getLocalStorage('vueuse-color-scheme').then((value) => {
            expect(value).to.eq('auto');
        });
    });

    it('Change Theme', () => {
        cy.visit('http://localhost:8080/#/settings');
        cy.getLocalStorage('vueuse-color-scheme').then((value) => {
            expect(value).to.eq('auto');
        });
        cy.contains('浅色').click();
        cy.getLocalStorage('vueuse-color-scheme').then((value) => {
            expect(value).to.eq('light');
        });
        cy.contains('深色').click();
        cy.getLocalStorage('vueuse-color-scheme').then((value) => {
            expect(value).to.eq('dark');
        });
        cy.contains('自动').click();
        cy.getLocalStorage('vueuse-color-scheme').then((value) => {
            expect(value).to.eq('auto');
        });
    });
});

describe('General Settings', () => {
    it('Hide Language Icon', () => {
        cy.visit('http://localhost:8080/#/settings');
        cy.get('[data-cy=languagePicker]').should('be.visible');
        cy.contains('语言切换').next().click();
        cy.get('[data-cy=languagePicker]').should('not.be.visible');
        cy.contains('语言切换').next().click();
        cy.get('[data-cy=languagePicker]').should('be.visible');
    });
});
