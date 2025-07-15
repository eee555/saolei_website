import i18n from '@/i18n';
import EmailCodeBlock from './emailCodeBlock.vue';
import $axios from '@/http';

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
const defaultProps = {
    type: 'register',
    email: 'test@example.com',
    emailState: 'success',
    modelValue: '',
};

Cypress.Commands.add('inputCaptcha', () => {
    cy.contains('Image captcha').next().find('input').type('1234');
});

describe('<EmailCodeBlock />', () => {
    it('Rendering', () => {
        cy.mockCaptchaRefresh();
        cy.mount(EmailCodeBlock, {
            ...mountOptions,
            props: defaultProps,
        });
        cy.contains('Image captcha').next().find('input').should('have.length', 1);
        cy.contains('Image captcha').next().find('img').should('have.length', 1);
        cy.contains('Email code').next().find('input').should('have.length', 1);
        cy.contains('Email code').next().find('button').should('have.length', 1);
    });

    it('Normal Flow', () => {
        cy.mockCaptchaRefresh();
        cy.mount(EmailCodeBlock, {
            ...mountOptions,
            props: defaultProps,
        });

        // Initial states
        cy.get('button').should('be.disabled');
        cy.get('button').should('have.text', 'Send');
        cy.get('[data-cy=emailCode]').should('be.disabled');
        cy.get('[data-cy=emailCode]').should('have.attr', 'placeholder', 'Captcha required');

        // Input captcha
        cy.inputCaptcha();
        cy.get('button').should('be.enabled');
        cy.get('button').should('have.text', 'Send');
        cy.get('[data-cy=emailCode]').should('be.enabled');
        cy.get('[data-cy=emailCode]').should('have.attr', 'placeholder', '');

        // Send email code
        cy.mockGetEmailCode();
        cy.get('button').click();
        cy.contains('Email is sent').next().next().click();
        cy.get('button').should('be.disabled');
        cy.get('[data-cy=emailCode]').should('be.enabled');
        cy.get('[data-cy=emailCode]').should('have.attr', 'placeholder', 'Please check your email');

        // Input email code
        cy.get('[data-cy=emailCode]').type('123456');
    });

    it('Incorrect captcha', () => {
        cy.mockCaptchaRefresh();
        cy.mount(EmailCodeBlock, {
            ...mountOptions,
            props: defaultProps,
        });
        cy.get('img').should('be.visible'); // wait for image to load

        // Input captcha
        cy.contains('Image captcha').next().find('input').type('1234');

        // Send email code
        cy.mockCaptchaRefresh({
            body: {
                status: 100,
                hashkey: 'refresh',
            },
        });
        cy.mockGetEmailCode({ 
            body: {
                type: 'error',
                object: 'captcha',
            },
        });
        cy.get('button').click();

        // Captcha auto refreshes
        cy.get('img').should('have.attr', 'src', 'http://127.0.0.1:8000/userprofile/captcha/image/refresh/');

        // Return to initial states
        cy.contains('Image captcha').next().get('input').should('be.empty');
        cy.get('[data-cy=emailCode]').should('be.disabled');
        cy.get('button').should('be.disabled');

        // Error message
        cy.contains('Image captcha').next().contains('Invalid captcha. Please input again').should('exist');
    });

    it('Failed to send email', () => {
        cy.clock();
        cy.mockCaptchaRefresh();
        cy.mount(EmailCodeBlock, {
            ...mountOptions,
            props: defaultProps,
        });
        cy.get('img').should('be.visible'); // wait for image to load

        // Input captcha
        cy.inputCaptcha();

        // Send email code
        cy.mockCaptchaRefresh({
            body: {
                status: 100,
                hashkey: 'refresh',
            },
        });
        cy.mockGetEmailCode({
            body: {
                type: 'error',
                object: 'email',
            },
        });
        cy.get('button').click();

        // Close error message
        cy.contains('Failed to send email').next().next().click();

        // Captcha auto refreshes
        cy.get('img').should('have.attr', 'src', 'http://127.0.0.1:8000/userprofile/captcha/image/refresh/');

        // Countdown
        cy.get('button').contains('(60)');
        cy.get('button').should('be.disabled');
        cy.tick(60000);
        cy.wait(0);
        cy.get('button').contains('(0)');
        cy.get('button').should('be.disabled');
        cy.tick(1000);
        cy.wait(0);

        // Return to initial states
        cy.contains('Image captcha').next().get('input').should('be.empty');
        cy.get('[data-cy=emailCode]').should('be.disabled');
        cy.get('button').should('be.disabled');
    });
});
