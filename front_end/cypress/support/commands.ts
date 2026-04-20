/// <reference types="cypress" />

import 'cypress-table';

declare global {
    namespace Cypress {
        interface Chainable {
            /**
             * cypress-get-table 插件，用于获取表格数据
             */
            getTable(): Chainable<Array<Record<string, string>>>;

            /**
             * 关闭所有通知
             */
            closeElNotifications(): void;

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

            extractTableData(): Chainable<string[][]>;
            shouldHaveState(expectedStates: (boolean | null)[]): void;
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

Cypress.Commands.add('closeElNotifications', () => {
    cy.get('.el-notification__closeBtn:visible').each(($el) => {
        cy.wrap($el).click();
    });
    cy.get('.el-notification__closeBtn:visible').should('not.exist');
});

Cypress.Commands.add('extractTableData', { prevSubject: 'element' }, (subject) => {
    const $table = Cypress.$(subject);
    const $rows = $table.find('> thead > tr, > tbody > tr, > tr');
    const tableData = [] as string[][];
    $rows.each((i, row) => {
        const $row = Cypress.$(row);
        const $cells = $row.find('> th, > td');
        const rowData = [] as string[];
        $cells.each((j, cell) => {
            rowData.push(Cypress.$(cell).text().trim());
        });
        tableData.push(rowData);
    });
    return cy.wrap(tableData);
});

Cypress.Commands.add(
    'shouldHaveState',
    { prevSubject: true },
    (subject: JQuery<HTMLElement>, expectedStates: (boolean | null)[]) => {
    // 验证长度是否匹配
        expect(subject.length).to.equal(
            expectedStates.length,
            `Expected ${expectedStates.length} checkboxes, but got ${subject.length}`,
        );

        // 遍历每个复选框进行状态断言
        cy.wrap(subject).each(($el, index) => {
            const expected = expectedStates[index];

            if (expected === false) {
                // 未选中：不应有 is-checked 和 is-indeterminate 类
                cy.wrap($el).should('not.have.class', 'is-checked');
                cy.wrap($el).should('not.have.class', 'is-indeterminate');
            } else if (expected === true) {
                // 选中：应有 is-checked 类，不应有 is-indeterminate 类
                cy.wrap($el).should('have.class', 'is-checked');
                cy.wrap($el).should('not.have.class', 'is-indeterminate');
            } else {
                // 半选：应有 is-indeterminate 类，不应有 is-checked 类
                cy.wrap($el).should('have.class', 'is-indeterminate');
                cy.wrap($el).should('not.have.class', 'is-checked');
            }
        });
    },
);

export {};
