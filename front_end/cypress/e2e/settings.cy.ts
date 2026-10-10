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
        // The load event can precede router readiness and Vue's theme initialization.
        cy.get('#app[data-v-app]', { timeout: Cypress.config('pageLoadTimeout') }).should('be.visible');
        cy.getLocalStorage('local').then((value) => {
            expect(value?.darkmode).to.be.true;
        });
        cy.window().its('localStorage').invoke('getItem', 'vueuse-color-scheme').should('eq', 'auto');
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
        cy.get('#app[data-v-app]', { timeout: Cypress.config('pageLoadTimeout') }).should('be.visible');
        cy.getLocalStorage('local').then((value) => {
            expect(value?.darkmode).to.be.false;
        });
        cy.window().its('localStorage').invoke('getItem', 'vueuse-color-scheme').should('eq', 'auto');
    });

    it('Change Theme', () => {
        cy.visit('/#/settings');
        cy.get('#app[data-v-app]', { timeout: Cypress.config('pageLoadTimeout') }).should('be.visible');
        cy.window().its('localStorage').invoke('getItem', 'vueuse-color-scheme').should('eq', 'auto');
        cy.contains('浅色').click();
        cy.window().its('localStorage').invoke('getItem', 'vueuse-color-scheme').should('eq', 'light');
        cy.contains('深色').click();
        cy.window().its('localStorage').invoke('getItem', 'vueuse-color-scheme').should('eq', 'dark');
        cy.contains('自动').click();
        cy.window().its('localStorage').invoke('getItem', 'vueuse-color-scheme').should('eq', 'auto');
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

    it('Hide Language Icon', () => {
        cy.visit('/#/settings');
        cy.get('[data-cy=languagePicker]').should('be.visible');
        cy.contains('dt', '语言切换').next('dd').find('.el-switch').click();
        cy.get('[data-cy=languagePicker]').should('not.be.visible');
        cy.contains('dt', '语言切换').next('dd').find('.el-switch').click();
        cy.get('[data-cy=languagePicker]').should('be.visible');
    });
});
