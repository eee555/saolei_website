describe('template spec', () => {
    it('menu navigation', () => {
        cy.visit('http://localhost:8080/');
        cy.url().should('eq', 'http://localhost:8080/#/');
        cy.getLocalStorage('local').then((value) => {
            value.language = 'zh-cn';
            cy.setLocalStorage('local', value);
        });
        cy.contains('排行榜').realClick();
        cy.url().should('eq', 'http://localhost:8080/#/ranking');
        cy.contains('录像').realClick();
        cy.url().should('eq', 'http://localhost:8080/#/video');
        cy.contains('教程').realClick();
        cy.url().should('eq', 'http://localhost:8080/#/guide');
        cy.contains('设置').realClick();
        cy.url().should('eq', 'http://localhost:8080/#/settings');
    });
});
