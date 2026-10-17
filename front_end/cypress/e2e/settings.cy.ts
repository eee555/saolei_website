describe('language setting', () => {
    const languages = {
        'zh-CN': '帮助',
        'zh-TW': '帮助', // fallback to zh-cn
        'en-GB': 'Help', // fallback to en
        fr: 'Help', // fallback to en
    };

    for (const [lang, label] of Object.entries(languages)) {
        it(`Detect Sys Language: ${lang}`, () => {
            cy.visit('/#/settings', {
                onBeforeLoad: (win) => {
                    Object.defineProperty(win.navigator, 'language', {
                        value: lang,
                        configurable: true,
                    });
                },
            });
            cy.get('[data-navigation-id=docs]').should('have.attr', 'aria-label', label);
        });
    }

    it('Change Language', () => {
        cy.visit('/#/settings');
        for (const [language, label] of [['dev', 'local.docs'], ['zh-cn', '帮助'], ['en', 'Help'], ['de', 'Hilfe'], ['pl', 'pomoc']] as const) {
            cy.get('[data-cy=languagePicker]').click();
            cy.get(`[data-navigation-id=language-${language}] button:visible`).click();
            cy.get('[data-navigation-id=docs]').should('have.attr', 'aria-label', label);
        }
    });
});

describe('Color Theme', () => {
    for (const dark of [true, false]) {
        it(`detects the system ${dark ? 'dark' : 'light'} theme`, () => {
            cy.visit('/#/settings', {
                onBeforeLoad: (win) => {
                    cy.stub(win, 'matchMedia').withArgs('(prefers-color-scheme: dark)').returns({
                        matches: dark,
                        addEventListener: () => undefined,
                        addListener: () => undefined,
                    });
                },
            });
            cy.get('#app[data-v-app]', { timeout: Cypress.config('pageLoadTimeout') }).should('be.visible');
            cy.get('html').should(dark ? 'have.class' : 'not.have.class', 'dark');
            cy.window().its('localStorage').invoke('getItem', 'local').should((value: string | null) => {
                const settings = JSON.parse(value ?? '{}') as { darkmode?: boolean };
                expect(settings.darkmode).to.equal(dark);
            });
            cy.window().its('localStorage').invoke('getItem', 'vueuse-color-scheme').should('eq', 'auto');
        });
    }

    it('switches themes from the toolbar and restores the choice after reloading', () => {
        cy.visit('/#/settings');
        cy.get('#app[data-v-app]', { timeout: Cypress.config('pageLoadTimeout') }).should('be.visible');
        cy.get('[data-cy=themePicker]').click();
        cy.get('[data-navigation-id=theme-light] button:visible').click();
        cy.window().its('localStorage').invoke('getItem', 'vueuse-color-scheme').should('eq', 'light');
        cy.get('html').should('not.have.class', 'dark');
        cy.get('[data-cy=themePicker]').click();
        cy.get('[data-navigation-id=theme-dark] button:visible').click();
        cy.window().its('localStorage').invoke('getItem', 'vueuse-color-scheme').should('eq', 'dark');
        cy.reload();
        cy.get('html').should('have.class', 'dark');
        cy.window().its('localStorage').invoke('getItem', 'vueuse-color-scheme').should('eq', 'dark');
        cy.get('[data-cy=themePicker]').click();
        cy.get('[data-navigation-id=theme-auto] button:visible').click();
        cy.window().its('localStorage').invoke('getItem', 'vueuse-color-scheme').should('eq', 'auto');
    });
});

describe('Navigation position', () => {
    it('keeps the selected layout after reloading', () => {
        cy.visit('/#/settings');
        cy.get('[data-cy=navigation-layout]').select('sidebar');
        cy.get('.site-shell').should('have.attr', 'data-navigation-layout', 'sidebar');
        cy.reload();
        cy.get('[data-cy=navigation-layout]').should('have.value', 'sidebar').select('top');
        cy.get('.site-shell').should('have.attr', 'data-navigation-layout', 'top');
        cy.url().should('include', '/#/settings');
    });
});

describe('General Settings', () => {
    it('persists third-party trust and supports toggling it with Space', () => {
        cy.visit('/#/settings');
        const trustLabel = 'https://strange-dust.github.io/minesweeper-replay-analyzer/';
        cy.contains('label', trustLabel).find('input').should('not.be.checked');
        cy.contains('label', trustLabel).click();
        cy.contains('label', trustLabel).find('input').should('be.checked');
        cy.window().its('localStorage').invoke('getItem', 'video-player-config').should((value: string | null) => {
            const config = JSON.parse(value ?? '{}') as { strangeDustTrust?: boolean };
            expect(config.strangeDustTrust).to.equal(true);
        });
        cy.reload();
        cy.contains('label', trustLabel).find('input').should('be.checked').focus();
        cy.realPress('Space');
        cy.contains('label', trustLabel).find('input').should('not.be.checked');
        cy.window().its('localStorage').invoke('getItem', 'video-player-config').should((value: string | null) => {
            const config = JSON.parse(value ?? '{}') as { strangeDustTrust?: boolean };
            expect(config.strangeDustTrust).to.equal(false);
        });
    });
});
