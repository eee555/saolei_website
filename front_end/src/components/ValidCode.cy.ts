import ValidCode from './ValidCode.vue';
import $axios from '@/http';
import i18n from '@/i18n';

const mountOptions = {
    global: {
        plugins: [i18n],
        config: {
            globalProperties: {
                $axios,
            },
        },
    },
};
const delay = 1000;

describe('<ValidCode />', () => {
    it('Loading and Rendering', () => {
        cy.mockCaptchaRefresh({ delay: delay });
        cy.mount(ValidCode, mountOptions);

        // Loading
        cy.get('img').should('not.exist');
        cy.contains('Loading').should('be.visible');

        // Rendering
        cy.get('img').should('have.attr', 'src', 'http://127.0.0.1:8000/userprofile/captcha/image/testkey/');
        cy.get('img').should('be.visible');
        cy.contains('Loading').should('not.exist');
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
