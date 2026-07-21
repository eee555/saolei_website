describe('language setting', () => {
    const languages = {
        'zh-CN': '帮助',
        'zh-TW': '帮助', // fallback to zh-cn
        'en-GB': 'Help', // fallback to en
        'en-US': 'Help', // fallback to en
        de: 'Hilfe',
        pl: 'pomoc',
        fr: 'Help', // fallback to en
    };

    for (const lang in languages) {
        it(`Detect Sys Language: ${lang}`, () => {
            cy.visit('/#/settings', {
                onBeforeLoad: (win) => {
                    Object.defineProperty((win as unknown as Window).navigator, 'language', {
                        value: lang,
                        configurable: true,
                    });
                },
            });
            // @ts-expect-error ts有毛病，认为lang可能不是languages的key
            cy.contains(languages[lang]);
        });
    }

    it('Change Language', () => {
        cy.visit('/#/settings');
        cy.get('[data-cy=languagePicker]').realClick();
        cy.contains('dev').filter(':visible').click();
        cy.contains('local.docs');
        cy.get('[data-cy=languagePicker]').realClick();
        cy.contains('简体中文').filter(':visible').click();
        cy.contains('帮助');
        cy.get('[data-cy=languagePicker]').realClick();
        cy.contains('English').filter(':visible').click();
        cy.contains('Help');
        cy.get('[data-cy=languagePicker]').realClick();
        cy.contains('Deutsch').filter(':visible').click();
        cy.contains('Hilfe');
        cy.get('[data-cy=languagePicker]').realClick();
        cy.contains('Polski').filter(':visible').click();
        cy.contains('pomoc');
    });
});

describe('Color Theme', () => {
    it('Detect Sys Dark Mode', () => {
        cy.visit('/#/settings', {
            onBeforeLoad: (win) => {
                cy.stub(win, 'matchMedia').withArgs('(prefers-color-scheme: dark)').returns({
                    matches: true,
                    addEventListener: () => undefined,
                    addListener: () => undefined,
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
        cy.visit('/#/settings', {
            onBeforeLoad: (win) => {
                cy.stub(win, 'matchMedia').withArgs('(prefers-color-scheme: dark)').returns({
                    matches: false,
                    addEventListener: () => undefined,
                    addListener: () => undefined,
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
        cy.visit('/#/settings');
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
        cy.visit('/#/settings');
        cy.get('[data-cy=languagePicker]').should('be.visible');
        cy.contains('语言切换').next().click();
        cy.get('[data-cy=languagePicker]').should('not.be.visible');
        cy.contains('语言切换').next().click();
        cy.get('[data-cy=languagePicker]').should('be.visible');
    });
});
