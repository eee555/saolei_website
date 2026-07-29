/* eslint-disable @typescript-eslint/method-signature-style */
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

const DANGERZONE_URL = 'http://127.0.0.1:8000/dangerzone';

interface DangerzoneUser {
    id: number;
    username: string;
    email?: string;
    password?: string;
    realname?: string;
}

interface DangerzoneVideo {
    user_id: number;
    identifier: string;
    level: string;
    timems: number;
    bv: number;
    state?: string;
    software?: string;
    mode?: string;
    file_size?: number;
    left?: number;
    right?: number;
    double?: number;
    left_ce?: number;
    right_ce?: number;
    double_ce?: number;
    path?: number;
    pluck?: number;
}

declare global {
    // eslint-disable-next-line @typescript-eslint/no-namespace
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
             * 调用 dangerzone API。仅在后端 E2E_TEST 模式可用。
             */
            dangerzonePost<T = unknown>(path: string, body?: object): Chainable<Response<T>>;

            /**
             * 注册测试用户。
             */
            registerUser(user: DangerzoneUser): Chainable<Response<unknown>>;

            /**
             * 创建测试录像。
             */
            createVideo(video: DangerzoneVideo): Chainable<Response<{ id: number }>>;

            /**
             * 创建测试标识。
             */
            createIdentifier(identifier: string, safe?: boolean): Chainable<Response<unknown>>;

            /**
             * 将测试标识绑定到指定用户，可选断言受影响录像数。
             */
            bindIdentifier(userId: number, identifier: string, expectedChangedCount?: number): Chainable<Response<{ changed_count: number }>>;

            /**
             * 将指定用户设为管理员。
             * @param {number} user_id - 用户ID
             * @example cy.setStaff(1);
             */
            setStaff(user_id: number): void;

            /**
             * 创建/加载一个记住登录状态的登录会话
             * @param {string} username - 用户名也作为会话名称
             * @param {string} password
             * @example cy.login('user', 'password');
             * cy.session('user);
             * */
            login(username: string, password: string): void;

            /**
             * 访问指定用户的个人主页
             * @param {number} userId - 用户ID
             * @param {string} [tab] - 可选参数，指定要访问的标签页，如'summary'、'record'、'accountlink'、'video'、'upload'
             * @example cy.visitUser(1);
             * */
            visitUser(userId: number, tab?: string): void;
        }
    }
}

Cypress.on('uncaught:exception', (err) => {
    console.error('Unhandled exception:', err.message);
    return false; // prevents the test from failing
});

Cypress.on('test:before:run', () => {
    Cypress.automation('remote:debugger:protocol', {
        command: 'Emulation.setTimezoneOverride',
        params: {
            timezoneId: 'Asia/Shanghai', // OR  'UTC'
        },
    });
});

beforeEach(() => {
    cy.intercept('GET', /^https?:\/\/(avatars\.githubusercontent\.com|minesweeper\.online|i2\.hdslb\.com)\/.*/, {
        fixture: 'test.png',
    });
});

Cypress.Commands.add('dangerzonePost', <T = unknown>(path: string, body: object = {}) => {
    return cy.request<T>({
        method: 'POST',
        url: `${DANGERZONE_URL}/${path}`,
        body,
    });
});

Cypress.Commands.add('registerUser', (user: DangerzoneUser) => {
    return cy.dangerzonePost('register', {
        id: user.id,
        username: user.username,
        email: user.email ?? `${user.username}@example.com`,
        password: user.password ?? 'password',
        realname: user.realname,
    });
});

Cypress.Commands.add('createVideo', (video: DangerzoneVideo) => {
    return cy.dangerzonePost<{ id: number }>('create_video', {
        state: 'd',
        software: 'e',
        mode: '00',
        file_size: 1024,
        left: 100,
        right: 50,
        double: 25,
        left_ce: 100,
        right_ce: 50,
        double_ce: 25,
        path: 1000,
        ...video,
    });
});

Cypress.Commands.add('createIdentifier', (identifier: string, safe = true) => {
    return cy.dangerzonePost('create_identifier', {
        identifier,
        safe,
    });
});

Cypress.Commands.add('bindIdentifier', (userId: number, identifier: string, expectedChangedCount?: number) => {
    return cy.dangerzonePost<{ changed_count: number }>('bind_identifier', {
        user_id: userId,
        identifier,
        safe: true,
    }).then((response) => {
        if (expectedChangedCount !== undefined) {
            expect(response.body.changed_count).to.eq(expectedChangedCount);
        }
        return response;
    });
});

Cypress.Commands.add('setStaff', (id: number) => {
    cy.request({
        method: 'POST',
        url: `${DANGERZONE_URL}/setstaff`,
        body: {
            id: id,
        },
    });
});

Cypress.Commands.add('login', (username: string, password: string) => {
    cy.session(username, () => {
        cy.visit('/#/settings');
        cy.contains(/^登录$/).click();

        cy.get('.el-dialog').then((dialog) => {
            cy.wrap(dialog).contains('用户名').next().find('input').type(username);
            cy.wrap(dialog).contains('密码').next().find('input').type(password);
            cy.wrap(dialog).contains('验证码').next().find('input').type('test{enter}');
            cy.wrap(dialog).contains('记住我').click();
            cy.wrap(dialog).find('button').contains('登录').click();
        });

        cy.get('.el-dialog').should('not.be.visible');
    });
});

Cypress.Commands.add('deleteUser', () => {
    cy.request('POST', `${DANGERZONE_URL}/delete_user`).then((response) => {
        expect(response.status).to.eq(200);
    });
});

Cypress.Commands.add('flushDatabase', () => {
    cy.request('POST', `${DANGERZONE_URL}/flush_database`).then((response) => {
        expect(response.status).to.eq(200);
    });
});

Cypress.Commands.add('visitUser', (userId: number, tab?: string) => {
    if (tab !== undefined) {
        cy.visit(`/#/player/${userId}/${tab}`);
    } else {
        cy.visit(`/#/player/${userId}`);
    }
});
