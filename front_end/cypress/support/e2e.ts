// ***********************************************************
// This example support/e2e.ts is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands';
import 'cypress-real-events';

declare global {
    namespace Cypress {
        interface Chainable {
            /**
             * 删除当前会话登录的用户。
             * @example cy.deleteUser();
             * */
            deleteUser(): void;

            /**
             * 清空数据库，恢复初始状态。
             * @example cy.flushDatabase();
             * */
            flushDatabase(): void;

            /**
             * 注册一个账号。如果该账号已存在，则报错。
             * @param {number} id - 用户ID
             * @param {string} username - 用户名
             * @param {string} email - 邮箱
             * @param {string} password - 密码
             * @example cy.register('user', 'user@example.com', 'password');
             * */
            register(id: number, username: string, email: string, password: string): void;


            /**
             * 创建/加载一个记住登录状态的登录会话
             * @param {string} username - 用户名也作为会话名称
             * @param {string} password
             * @example cy.login('user', 'password');
             * cy.session('user);
             * */
            login(username: string, password: string): void;
        }
    }
}

Cypress.on('uncaught:exception', (err, _runnable) => {
    console.error('Unhandled exception:', err.message);
    return false; // prevents the test from failing
});

Cypress.Commands.add('register', (id: number, username: string, email: string, password: string) => {
    cy.request({
        method: 'POST',
        url: 'http://127.0.0.1:8000/dangerzone/register/',
        body: {
            id: id,
            username: username,
            email: email,
            password: password,
        },
    });
});

Cypress.Commands.add('login', (username: string, password: string) => {
    cy.session(username, () => {
        cy.visit('/#/settings');
        cy.contains(/^登录$/).click();
        cy.contains('用户名').next().find('input').type(username);
        cy.contains('密码').next().find('input').type(password);
        cy.contains('验证码').next().find('input').type('test{enter}');
        cy.contains('记住我').click();
        cy.contains('用户登录').parent().parent().find('button').contains('登录').click();
        cy.contains('用户登录').should('not.be.visible'); // wait for the popup to disappear
    });
});

Cypress.Commands.add('deleteUser', () => {
    cy.request('POST', 'http://127.0.0.1:8000/dangerzone/delete_user/').then((response) => {
        expect(response.status).to.eq(200);
    });
});

Cypress.Commands.add('flushDatabase', () => {
    cy.request('POST', 'http://127.0.0.1:8000/dangerzone/flush_database/').then((response) => {
        expect(response.status).to.eq(200);
    });
});
