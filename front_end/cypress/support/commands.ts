/// <reference types="cypress" />
// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
//
declare global {
    namespace Cypress {
        interface Chainable {
            /**
             * 获取本地存储的值
             * @param key - 本地存储的键
             * @example cy.getLocalStorage('authToken')
             */
            getLocalStorage(key: string): Chainable;

            /**
             * 设置本地存储的值
             * @param key - 本地存储的键
             * @param value - 要存储的值
             * @example cy.setLocalStorage('authToken', 'abc123')
             */
            setLocalStorage(key: string, value: string): void;

            /**
             * 模拟验证码刷新
             * @param options - 请求选项
             * @example cy.mockCaptchaRefresh({})
             */
            mockCaptchaRefresh(options?: any): void;

            /**
             * 模拟获取邮件验证码
             * @param options - 请求选项
             * @example cy.mockGetEmailCode({})
             */
            mockGetEmailCode(options?: any): void;

            /**
             * 模拟登录
             * @example cy.mockLogin()
             */
            mockLogin(): void;

            /**
             * 模拟注册
             * @example cy.mockRegister()
             */
            mockRegister(): void;
        }
    }
}

Cypress.Commands.add('getLocalStorage', (key: string) => {
    return cy.window().then((win) => {
        const value = win.localStorage.getItem(key);
        try {
            return value ? JSON.parse(value) : null;
        } catch (_e) {
            // If not valid JSON, return the raw string
            return value;
        }
    });
});

Cypress.Commands.add('setLocalStorage', (key: string, value: string) => {
    cy.window().then((win) => {
        win.localStorage.setItem(key, value);
    });
});

Cypress.Commands.add('mockCaptchaRefresh', (options) => {
    let captchaRefreshCount = 0;
    cy.intercept('GET', '/userprofile/refresh_captcha/', (req) => {
        captchaRefreshCount += 1;
        req.reply({
            statusCode: 200,
            headers: { 'Content-Type': 'application/json' },
            body: {
                status: 100,
                hashkey: `testkey${captchaRefreshCount}`,
            },
            ...options,
        });
    }).as('captchaRefresh');
    cy.intercept('GET', '/userprofile/captcha/image/**', {
        fixture: 'test.png',
    }).as('testImage');
});

Cypress.Commands.add('mockGetEmailCode', (options) => {
    cy.intercept('POST', '/userprofile/get_email_captcha/', {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: {
            type: 'success',
            hashkey: 'testkey',
        },
        ...options,
    }).as('getEmailCode');
});

Cypress.Commands.add('mockRegister', () => {
    cy.intercept('POST', '/userprofile/register', (req) => {
        const params = new URLSearchParams(req.body);
        const email_captcha = params.get('email_captcha');

        if (email_captcha !== '123456') {
            req.reply({
                type: 'error',
                object: 'emailCode',
            });
            return;
        }
        req.reply({
            type: 'success',
            user: {},
        });
    });
});

Cypress.Commands.add('mockLogin', () => {
    cy.intercept('POST', '/userprofile/login/', (req) => {
        const params = new URLSearchParams(req.body);
        const username = params.get('username');
        const password = params.get('password');
        const captcha = params.get('captcha');
        if (captcha !== 'test') {
            req.reply({
                'type': 'error',
                'object': 'login',
                'category': 'captcha',
            });
            return;
        }
        if (username === 'test' && password === 'test') {
            req.reply({
                'type': 'success',
                'user': {},
            });
        } else {
            req.reply({
                'type': 'error',
                'object': 'login',
                'category': 'password',
            });
        }
    });
});

export {};
