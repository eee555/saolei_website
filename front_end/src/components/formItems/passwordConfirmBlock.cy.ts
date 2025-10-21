import passwordConfirmBlock from './passwordConfirmBlock.vue';

import i18n from '@/i18n';

const mountOptions = {
    props: {
        modelValue: '',
    },
    global: {
        plugins: [i18n],
    },
};

const errorColor = 'rgb(245, 108, 108)';
const successColor = 'rgb(168, 171, 178)';

function findPasswordInput() {
    return cy.contains('Password').next().find('input');
}
function findConfirmPasswordInput() {
    return cy.contains('Confirm password').next().find('input');
}

function expectPasswordValidationError(msg: string) {
    cy.contains('Password').next().contains(msg).should('have.css', 'color', errorColor);
}
function expectConfirmPasswordValidationError(msg: string) {
    cy.contains('Confirm password').next().contains(msg).should('have.css', 'color', errorColor);
}
function expectPasswordValidationSuccess() {
    cy.contains('Password').next().find('i').last().should('have.css', 'color', successColor);
}
function expectConfirmPasswordValidationSuccess() {
    cy.contains('Confirm password').next().find('i').last().should('have.css', 'color', successColor);
}

describe('<passwordConfirmBlock />', () => {
    it('Rendering', () => {
        // see: https://on.cypress.io/mounting-vue
        cy.mount(passwordConfirmBlock, mountOptions);
        findPasswordInput().should('have.attr', 'type', 'password');
        findConfirmPasswordInput().should('have.attr', 'type', 'password');
    });

    it('Validation', () => {
        cy.mount(passwordConfirmBlock, mountOptions);

        cy.log('Minimum length');
        findPasswordInput().type('1234{enter}');
        expectPasswordValidationError('Password requires at least 6 characters');

        cy.log('Password required');
        findPasswordInput().clear();
        findPasswordInput().type('{enter}');
        expectPasswordValidationError('Password required');

        cy.log('Password success');
        findPasswordInput().type('123456{enter}');
        expectPasswordValidationSuccess();

        cy.log('Confirm password mismatch');
        findPasswordInput().type('123456{enter}');
        findConfirmPasswordInput().type('123457{enter}');
        expectConfirmPasswordValidationError('Mismatches password');

        cy.log('Confirm password success');
        findConfirmPasswordInput().clear();
        findConfirmPasswordInput().type('123456{enter}');
        expectConfirmPasswordValidationSuccess();
    });
});
