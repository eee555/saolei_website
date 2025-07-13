import ValidCode from './ValidCode.vue';
import $axios from '@/http';
import i18n from '@/i18n';

Cypress.on('uncaught:exception', (err) => {
    if (err.message.includes('Cannot read properties of undefined (reading \'app\')')) {
        return false;
    }
});

const mountOptions = {
    global: {
        plugins: [i18n],
        config: {
            globalProperties: {
                $axios,
            },
        },
        provide: {
            app: {},
        },
    },
};
const delay = 1000;

describe('<ValidCode />', () => {
    it('Loading and Rendering', () => {
        cy.intercept('GET', 'http://127.0.0.1:8000/userprofile/captcha/image/testkey/', {
            fixture: 'test.png',
        }).as('testImage');
        cy.intercept('GET', 'http://127.0.0.1:8000/userprofile/refresh_captcha/', {
            statusCode: 200,
            headers: { 'content-type': 'application/json' },
            body: {
                status: 100,
                hashkey: 'testkey',
            },
            delay: delay,
        }).as('defaultCaptcha');
        cy.mount(ValidCode, mountOptions);
        cy.contains('Loading').should('be.visible');
        cy.get('img').should('have.attr', 'src', 'http://127.0.0.1:8000/userprofile/captcha/image/testkey/');
        cy.get('img').should('be.visible');
    });

    it('410 Error', () => {
        cy.intercept('GET', '/userprofile/refresh_captcha/', {
            statusCode: 410,
        }).as('error410');
        cy.mount(ValidCode, mountOptions);
        cy.contains('An unexpected error occurred.');
        cy.contains('Failed').should('be.visible');
    });
});
