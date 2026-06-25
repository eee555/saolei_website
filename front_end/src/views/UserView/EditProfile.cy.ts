import EditProfile from './EditProfile.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { pinia } from '@/store/create';
import { UserProfile } from '@/utils/userprofile';

function mountOptions(props?: any) {
    return {
        props: props,
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

function findLocalNameInput() {
    return cy.contains('Local Name').parent().next().find('input');
}

function findFirstNameInput() {
    return cy.contains('International Name').parent().next().find('input').eq(0);
}

function findLastNameInput() {
    return cy.contains('International Name').parent().next().find('input').eq(1);
}

function findSignatureInput() {
    return cy.contains('Signature').parent().next().find('textarea');
}

function mockUpdateResponse(body: any) {
    cy.intercept('POST', '/api/userprofile/update_profile', {
        statusCode: 200,
        body: body,
    }).as('updateProfile');
}

describe('EditProfile', () => {
    beforeEach(() => {
        cy.clock(new Date('2025-01-01T00:00:00Z'));
    });

    it('Render', () => {
        cy.mount(EditProfile, mountOptions());

        cy.contains('Real Name').next().contains('Your real name cannot be changed once set');

        cy.contains('Local Name').next().contains('Fill in your full name in your local language').parent().next().find('input');

        cy.contains('International Name').next().contains('Fill in your given name and family name in English').parent().next().find('input').should('have.length', 2);

        cy.contains('Signature').next().contains('modify your signature').parent().next().find('textarea');

        cy.get('button').eq(0).contains('Save');
        cy.get('button').eq(1).contains('Cancel');
    });

    describe('Local name', () => {
        it('Disabled', () => {
            cy.mount(EditProfile, mountOptions({
                user: new UserProfile({ realname: 'realname' }),
                isEditing: true,
            }));

            findLocalNameInput().should('be.disabled');
        });

        it('Update', () => {
            const user = new UserProfile({
                firstname: 'firstname',
                lastname: 'lastname',
                signature: 'signature',
            });

            mockUpdateResponse({
                realname: { type: 'success' },
                signature: null,
                firstname: null,
                lastname: null,
            });

            cy.mount(EditProfile, mountOptions({
                user: user,
                isEditing: true,
            }));

            findLocalNameInput().type('realname');
            cy.get('button').contains('Save').click();

            cy.wait('@updateProfile').interceptFormData((formData) => {
                expect(formData.realname).to.equal('realname');
                expect(formData.signature).to.be.undefined;
                expect(formData.firstname).to.be.undefined;
                expect(formData.lastname).to.be.undefined;
            });

            cy.then(() => {
                expect(user.realname).to.equal('realname');
            });
        });
    });

    describe('International name', () => {
        it('First name - disabled', () => {
            cy.mount(EditProfile, mountOptions({
                user: new UserProfile({ firstname: 'firstname' }),
                isEditing: true,
            }));

            findFirstNameInput().should('be.disabled');
        });

        it('First name - update', () => {
            const user = new UserProfile({
                realname: 'realname',
                lastname: 'lastname',
                signature: 'signature',
            });

            mockUpdateResponse({
                realname: null,
                signature: null,
                firstname: { type: 'success' },
                lastname: null,
            });

            cy.mount(EditProfile, mountOptions({
                user: user,
                isEditing: true,
            }));

            findFirstNameInput().type('firstname');
            cy.get('button').contains('Save').click();

            cy.wait('@updateProfile').interceptFormData((formData) => {
                expect(formData.firstname).to.equal('firstname');
                expect(formData.realname).to.be.undefined;
                expect(formData.signature).to.be.undefined;
                expect(formData.lastname).to.be.undefined;
            });

            cy.then(() => {
                expect(user.firstname).to.equal('firstname');
            });
        });

        it('Last name - disabled', () => {
            cy.mount(EditProfile, mountOptions({
                user: new UserProfile({ lastname: 'lastname' }),
                isEditing: true,
            }));

            findLastNameInput().should('be.disabled');
        });

        it('Last name - update', () => {
            const user = new UserProfile({
                realname: 'realname',
                firstname: 'firstname',
                signature: 'signature',
            });

            mockUpdateResponse({
                realname: null,
                signature: null,
                firstname: null,
                lastname: { type: 'success' },
            });

            cy.mount(EditProfile, mountOptions({
                user: user,
                isEditing: true,
            }));

            findLastNameInput().type('lastname');
            cy.get('button').contains('Save').click();

            cy.wait('@updateProfile').interceptFormData((formData) => {
                expect(formData.lastname).to.equal('lastname');
                expect(formData.realname).to.be.undefined;
                expect(formData.signature).to.be.undefined;
                expect(formData.firstname).to.be.undefined;
            });

            cy.then(() => {
                expect(user.lastname).to.equal('lastname');
            });
        });
    });

    describe('Signature', () => {
        it('Disabled - no budget', () => {
            cy.mount(EditProfile, mountOptions({
                user: new UserProfile({ left_signature_n: 0 }),
                isEditing: true,
                expTimeMs: 30000,
            }));

            findSignatureInput().should('be.disabled');
            cy.contains('You gain one chance to modify your signature each month. You have no chance remaining. Next available on: 2025-02-01 08:00:00');
        });

        it('Disabled - exp sup 200', () => {
            cy.mount(EditProfile, mountOptions({
                user: new UserProfile({ left_signature_n: 1 }),
                isEditing: true,
                expTimeMs: 999999,
            }));

            findSignatureInput().should('be.disabled');
            cy.contains('Achieve expert sub200 to change signature');
        });

        it('Update', () => {
            const user = new UserProfile({
                realname: 'realname',
                firstname: 'firstname',
                lastname: 'lastname',
                signature: 'signature',
                left_signature_n: 1,
            });

            mockUpdateResponse({
                realname: null,
                firstname: null,
                lastname: null,
                signature: { type: 'success' },
            });

            cy.mount(EditProfile, mountOptions({
                user: user,
                isEditing: true,
                expTimeMs: 30000,
            }));

            findSignatureInput().clear();
            findSignatureInput().type('Updated signature');
            cy.get('button').contains('Save').click();

            cy.wait('@updateProfile').interceptFormData((formData) => {
                expect(formData.signature).to.equal('Updated signature');
                expect(formData.realname).to.be.undefined;
                expect(formData.firstname).to.be.undefined;
                expect(formData.lastname).to.be.undefined;
            });

            cy.then(() => {
                expect(user.signature).to.equal('Updated signature');
            });
        });

        it('Error - censorship.unknown', () => {
            mockUpdateResponse({
                realname: null,
                firstname: null,
                lastname: null,
                signature: {
                    type: 'error',
                    object: 'censorship',
                    category: 'unknown',
                },
            });

            cy.mount(EditProfile, mountOptions({
                user: new UserProfile({ left_signature_n: 1 }),
                isEditing: true,
                expTimeMs: 30000,
            }));

            findSignatureInput().type('censorship.unknown');
            cy.get('button').contains('Save').click();

            cy.contains('Unknown error occurred in censorship. Please contact a moderator');
        });

        it('Error - censorship.illegal', () => {
            mockUpdateResponse({
                realname: null,
                firstname: null,
                lastname: null,
                signature: {
                    type: 'error',
                    object: 'censorship',
                    category: 'illegal',
                },
            });

            cy.mount(EditProfile, mountOptions({
                user: new UserProfile({ left_signature_n: 1 }),
                isEditing: true,
                expTimeMs: 30000,
            }));

            findSignatureInput().type('censorship.illegal');
            cy.get('button').contains('Save').click();

            cy.contains('The content is blocked by censorship. Please change the text or contact a moderator for manual review');
        });
    });

    describe('Buttons', () => {
        it('Cancel', () => {
            cy.mount(EditProfile, mountOptions({
                user: new UserProfile(),
                isEditing: true,
            }));

            cy.get('button').contains('Cancel').click();
            cy.get('@vue').should((wrapper: ComponentWrapper<typeof EditProfile>) => {
                expect(wrapper.emitted('update:isEditing')).to.deep.equal([[false]]);
            });
        });

        it('Save - nothing changed', () => {
            cy.intercept('POST', '/api/userprofile/update_profile', () => {
                throw new Error('Unexpected API call');
            }).as('updateProfile');

            cy.mount(EditProfile, mountOptions({
                user: new UserProfile(),
                isEditing: true,
            }));

            cy.get('button').contains('Save').click();
            cy.get('@vue').then((wrapper: ComponentWrapper<typeof EditProfile>) => {
                expect(wrapper.emitted('update:isEditing')).to.deep.equal([[false]]);
            });
        });
    });
});
