describe('template spec', () => {
    it('menu navigation', () => {
        cy.visit('http://localhost:8080/');
        cy.get('#app[data-v-app]', { timeout: Cypress.config('pageLoadTimeout') }).should('be.visible');
        cy.url().should('eq', 'http://localhost:8080/#/');
        cy.contains('.el-header .el-menu-item', '排行榜').click();
        cy.url().should('contain', 'http://localhost:8080/#/ranking');
        cy.contains('.el-header .el-menu-item', '录像').click();
        cy.url().should('eq', 'http://localhost:8080/#/video');
        cy.contains('.el-header .el-menu-item', '帮助');
        cy.contains('.el-header .el-menu-item', '设置').click();
        cy.url().should('eq', 'http://localhost:8080/#/settings');
    });
});
