import { showInvisibleIdentifiers } from './identifierDisplay';
import IdentifierManager from './IdentifierManager.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { store } from '@/store';
import { pinia } from '@/store/create';
import { UserProfile } from '@/utils/userprofile';

// 模拟用户工厂函数
function createMockUser(id: number, identifiers?: string[]): UserProfile {
    const user = new UserProfile();
    user.id = id;
    user.identifiers = identifiers;
    return user;
}

// 快速挂载组件的辅助函数（假设已配置 i18n）
function mountOption(user: UserProfile) {
    return {
        props: {
            user,
        },
        global: {
            plugins: [i18n, pinia],
            config: {
                globalProperties: {
                    $axios,
                },
            },
        },
    };
}

function mockGetIdentifiers(body: string[] = [], as = 'getIdentifiers') {
    cy.intercept('GET', '/api/userprofile/identifier*', {
        statusCode: 200,
        body: body,
    }).as(as);
}

function mockDelIdentifier(body: object, as = 'delIdentifier') {
    cy.intercept('POST', '/identifier/del/', {
        statusCode: 200,
        body: body,
    }).as(as);
}

function mockAddIdentifier(body: object, as = 'addIdentifier') {
    cy.intercept('POST', '/identifier/add/', {
        statusCode: 200,
        body: body,
    }).as(as);
}

describe('IdentifierManager.vue', () => {
    beforeEach(() => {
        showInvisibleIdentifiers.value = false;
        store.user = createMockUser(1);
        store.new_identifier = false;
    });

    it('hides editing controls for another player', () => {
        cy.mount(IdentifierManager, mountOption(createMockUser(2, ['abc', 'def'])));

        cy.get('.el-table__body').extractTableData().should('deep.equal', [['abc', ''], ['def', '']]);

        cy.get('.el-input').should('not.exist');
        cy.get('.el-table__body button[aria-label="Delete identifier"]').should('not.exist');

        cy.get('.el-table__body').find('.pi-copy').should('have.length', 2);
    });

    it('copies and deletes the original identifier while escape markers are visible', () => {
        const identifier = ' a\u200B ';
        mockDelIdentifier({ value: 3 });
        cy.mount(IdentifierManager, mountOption(createMockUser(1, [identifier])));
        cy.window().then((win) => {
            const copy = cy.stub(win.navigator.clipboard, 'writeText').as('copy');
            copy.resolves();
        });
        cy.contains('label', 'Show invisible characters').find('input').check();
        cy.get('.el-table__body .identifier-text').should('have.text', '␠a⟦U+200B⟧␠');
        cy.get('.el-table__body button[aria-label="Copy"]').click();
        cy.get('@copy').should('have.been.calledOnceWith', identifier);
        cy.closeElNotifications();
        cy.get('.el-table__body button[aria-label="Delete identifier"]').click();
        cy.wait('@delIdentifier').its('request.body').then((body: string) => {
            expect(new URLSearchParams(body).get('identifier')).to.equal(identifier);
        });
        cy.contains('Identifier Deleted');
        cy.contains('3 videos have been processed');
        cy.closeElNotifications();
        cy.get('.el-table__body').extractTableData().should('deep.equal', [['', '']]);
    });

    it('Add Identifier - Success', () => {
        mockGetIdentifiers();
        mockAddIdentifier({
            type: 'success',
            value: 5,
        });
        cy.mount(IdentifierManager, mountOption(createMockUser(1)));

        cy.get('.el-input input').type('new-123');
        cy.get('.el-table__body button[aria-label="add identifier"]').focus();
        cy.realPress('Enter');

        cy.contains('Identifier Added');
        cy.contains('5 videos have been processed');
        cy.closeElNotifications();

        cy.get('.el-input input').should('have.value', '');
        cy.get('.el-table__body').extractTableData().should('deep.equal', [['new-123', ''], ['', '']]);
    });

    it('Add Identifier - Not Found', () => {
        mockGetIdentifiers();
        mockAddIdentifier({
            type: 'error',
            category: 'notFound',
        });

        cy.mount(IdentifierManager, mountOption(createMockUser(1)));

        cy.get('.el-input input').type('missing-id');
        cy.get('.el-table__body button[aria-label="add identifier"]').click();

        cy.contains('You do not have any video of the identifier');
        cy.closeElNotifications();

        cy.get('.el-input input').should('have.value', '');
        cy.get('.el-table__body').extractTableData().should('deep.equal', [['', '']]);
    });

    it('Add Identifier - Occupied', () => {
        mockGetIdentifiers();
        mockAddIdentifier({
            type: 'error',
            category: 'conflict',
            value: 'other_user',
        });

        cy.mount(IdentifierManager, mountOption(createMockUser(1)));

        cy.get('.el-input input').type('taken-id');
        cy.get('.el-table__body button[aria-label="add identifier"]').click();

        cy.contains('Identifier Conflict');
        cy.closeElNotifications();

        cy.get('.el-input input').should('have.value', '');
        cy.get('.el-table__body').extractTableData().should('deep.equal', [['', '']]);
    });

    describe('Watch User Id', () => {
        it('Refresh', () => {
            cy.mount(IdentifierManager, mountOption(createMockUser(2, ['a'])));
            cy.get('.el-table__body').extractTableData().should('deep.equal', [['a', '']]);

            mockGetIdentifiers(['new-b']);

            cy.get('@vue').then((wrapper: ComponentWrapper<typeof IdentifierManager>) => {
                void wrapper.setProps({
                    user: createMockUser(3),
                });
            });
            cy.wait('@getIdentifiers');
            cy.get('.el-table__body').extractTableData().should('deep.equal', [['new-b', '']]);
        });
    });
});
