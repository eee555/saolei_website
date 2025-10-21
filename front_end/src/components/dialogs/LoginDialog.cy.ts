import type {} from '@cy/support/component';

import LoginDialog from './LoginDialog.vue';

import $axios from '@/http';
import i18n from '@/i18n';

const mountOptions = {
    props: {
        modelValue: true,
    },
    global: {
        plugins: [i18n],
        config: {
            globalProperties: {
                $axios,
            },
        },
    },
};

function expectCaptchaRefresh(count: number) {
    cy.contains('Captcha').next().find('img').should('have.attr', 'src', `http://127.0.0.1:8000/userprofile/captcha/image/testkey${count}/`);
}

describe('<LoginDialog />', () => {
    beforeEach(() => {
        cy.mockLogin();
        cy.mockCaptchaRefresh();
    });

    it('Rendering', () => {
        cy.mount(LoginDialog, mountOptions);
        cy.contains('Login');
        cy.contains('Username').next().find('input').should('have.attr', 'type', 'text');
        cy.contains('Password').next().find('input').should('have.attr', 'type', 'password');
        cy.contains('Captcha').next().find('input').should('have.attr', 'type', 'text');
        cy.contains('Captcha').next().find('img');
        cy.contains('Keep me logged in').find('input').should('have.attr', 'type', 'checkbox');
        cy.contains('Forget password?');
        cy.get('button').should('have.text', 'Log in');
    });

    it('Normal Flow', () => {
        cy.mount(LoginDialog, mountOptions);
        cy.contains('Username').next().type('test');
        cy.contains('Password').next().type('test');
        cy.contains('Captcha').next().type('test');
        cy.contains('Log in').click();

        cy.contains('Invalid captcha. Please input again').should('not.exist');
        cy.contains('Invalid username or password').should('not.exist');
    });

    it('Closing with Icon', () => {
        // 点击右上角关闭
        cy.mount(LoginDialog, mountOptions);
        cy.contains('Login').next().click();
        cy.contains('Login').should('not.be.visible');
    });

    it('Closing by Clicking Outside', () => {
        // 点击空白处关闭
        cy.mount(LoginDialog, mountOptions);
        cy.get('body').click(0, 0);
        cy.contains('Login').should('not.be.visible');
    });

    it('Username Validation', () => {
        cy.mount(LoginDialog, mountOptions);

        // Normal username
        cy.contains('Username').next().type('test');
        cy.contains('Username').click();
        cy.contains('Username').next().find('input').should('have.value', 'test');

        // Username required
        cy.contains('Username').next().find('input').clear();
        cy.contains('Username required');

        // Username too long
        cy.contains('Username').next().type('abcdefghijklmnopqrstuvwxyz');
        cy.contains('Username').next().find('input').should('have.value', 'abcdefghijklmnopqrst');
    });

    it('Password Validation', () => {
        cy.mount(LoginDialog, mountOptions);

        // Normal password
        cy.contains('Password').next().type('test');
        cy.contains('Password').click();
        cy.contains('Password').next().find('input').should('have.value', 'test');

        // Password required
        cy.contains('Password').next().find('input').clear();
        cy.contains('Password required');
    });

    it('Captcha Validation', () => {
        cy.mount(LoginDialog, mountOptions);

        // Normal captcha
        cy.contains('Captcha').next().find('input').type('test');
        cy.contains('Captcha').click();
        cy.contains('Captcha').next().find('input').should('have.value', 'test');

        // Captcha required
        cy.contains('Captcha').next().find('input').clear();
        cy.contains('Captcha required');
    });

    it('Incorrect Captcha', () => {
        cy.mount(LoginDialog, mountOptions);
        cy.contains('Username').next().type('test');
        cy.contains('Password').next().type('test');
        cy.contains('Captcha').next().find('input').type('maga');

        cy.contains('Log in').click();
        cy.contains('Invalid captcha. Please input again');
        expectCaptchaRefresh(2);
    });

    it('Incorrect Username or Password', () => {
        cy.mount(LoginDialog, mountOptions);
        cy.contains('Username').next().type('test');
        cy.contains('Password').next().type('password');
        cy.contains('Captcha').next().find('input').type('test');

        cy.contains('Log in').click();
        cy.contains('Invalid username or password');
        expectCaptchaRefresh(2);
        cy.contains('Captcha required');
    });
});
