function visitWithStartupScript(script: string) {
    cy.intercept('GET', 'http://localhost:8080/', (request) => {
        request.continue((response) => {
            if (typeof response.body !== 'string') return;
            response.body = response.body.replace('<head>', `<head><script>${script}</script>`);
        });
    });
    cy.visit('/');
}

describe('outdated browser', () => {
    it('shows an upgrade message instead of the resource loader when toReversed is missing', () => {
        visitWithStartupScript('Reflect.deleteProperty(Array.prototype, "toReversed");');

        cy.contains('您的浏览器版本过低，请使用最新的chrome浏览器。').should('be.visible');
        cy.contains('正在加载资源').should('not.be.visible');
    });

    it('replaces the resource loader when startup throws toReversed is not a function', () => {
        cy.on('uncaught:exception', (error) => !error.message.includes('toReversed'));
        visitWithStartupScript([
            'Object.defineProperty(Array.prototype, "toReversed", {',
            'configurable: true, writable: true,',
            'value: function () { throw new TypeError("toReversed is not a function"); }',
            '});',
        ].join(''));

        cy.contains('您的浏览器版本过低，请使用最新的chrome浏览器。').should('be.visible');
        cy.contains('正在加载资源').should('not.be.visible');
    });

    it('loads the app when the browser provides toReversed', () => {
        cy.visit('/');
        cy.get('#app[data-v-app]', { timeout: Cypress.config('pageLoadTimeout') }).should('be.visible');
        cy.contains('您的浏览器版本过低，请使用最新的chrome浏览器。').should('not.exist');
    });
});
