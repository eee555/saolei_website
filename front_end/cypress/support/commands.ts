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
// declare global {
//   namespace Cypress {
//     interface Chainable {
//       login(email: string, password: string): Chainable<void>
//       drag(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       dismiss(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       visit(originalFn: CommandOriginalFn, url: string, options: Partial<VisitOptions>): Chainable<Element>
//     }
//   }
// }

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
    cy.intercept('GET', '/userprofile/refresh_captcha/', {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: {
            status: 100,
            hashkey: 'testkey',
        },
        ...options,
    }).as('captchaRefresh');
    cy.intercept('GET', '/userprofile/captcha/image/testkey/', {
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
