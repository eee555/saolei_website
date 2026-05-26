
import Avatar from './Avatar.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { pinia } from '@/store/create';
import { UserProfile } from '@/utils/userprofile';

function mountOptions(props: any) {
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

const largeFile = Cypress.Buffer.from('x'.repeat(400 * 1024));
const validFile = Cypress.Buffer.from('x');

describe('<Avatar />', () => {
    beforeEach(() => {
        cy.clock(new Date('2025-01-01T00:00:01Z'));
    });

    it('Rendering', () => {
        cy.mount(Avatar, mountOptions({
            user: new UserProfile(),
            isSelf: true,
        }));

        cy.get('img').should('have.attr', 'src').and('include', '?v=0');
    });

    it('Guest view', () => {
        cy.mount(Avatar, mountOptions({
            user: new UserProfile(),
            isSelf: false,
            expTimeMs: 30000,
        }));

        cy.get('img').realHover();
        cy.get('[id^=tippy-]').should('not.exist');
    });

    it('Tooltip - et sup 200', () => {
        cy.mount(Avatar, mountOptions({
            user: new UserProfile(),
            isSelf: true,
            expTimeMs: 999999,
        }));

        cy.get('img').realHover();
        cy.contains('Achieve expert sub200 to set avatar');
    });

    it('Tooltip - no budget', () => {
        cy.mount(Avatar, mountOptions({
            user: new UserProfile({ left_avatar_n: 0 }),
            isSelf: true,
            expTimeMs: 30000,
        }));

        cy.get('img').realHover();
        cy.contains('Avatar can be changed once every year. Next available time: 2026-01-01 08:00:00');
    });

    it('Tooltip - normal', () => {
        cy.mount(Avatar, mountOptions({
            user: new UserProfile({ left_avatar_n: 1, last_change_avatar: '2024-01-01T00:00:00Z' }),
            isSelf: true,
            expTimeMs: 30000,
        }));

        cy.get('img').realHover();
        cy.contains('Click to change avatar (2 times left)');
    });

    it('Upload - large file', () => {
        cy.mount(Avatar, mountOptions({
            user: new UserProfile({ left_avatar_n: 1 }),
            isSelf: true,
            expTimeMs: 30000,
        }));

        cy.get('input[type=file]').selectFile([{ contents: largeFile }], { force: true });
        cy.contains('Avatar file is too large. Please upload a file smaller than 300KB');
        cy.closeElNotifications();
    });

    it('Upload - database validation', () => {
        cy.intercept('POST', '/api/userprofile/update_avatar', {
            body: {
                type: 'error',
                object: 'avatar',
                category: 'validation',
            },
        });

        cy.mount(Avatar, mountOptions({
            user: new UserProfile({ left_avatar_n: 1 }),
            isSelf: true,
            expTimeMs: 30000,
        }));

        cy.get('input[type=file]').selectFile([{ contents: validFile }], { force: true });
        cy.contains('File rejected by database. Please check the file format or contact a moderator');
        cy.closeElNotifications();
    });

    it('Upload - censorship failure', () => {
        cy.intercept('POST', '/api/userprofile/update_avatar', {
            body: {
                type: 'error',
                object: 'censorship',
                category: 'unknown',
            },
        });

        cy.mount(Avatar, mountOptions({
            user: new UserProfile({ left_avatar_n: 1 }),
            isSelf: true,
            expTimeMs: 30000,
        }));

        cy.get('input[type=file]').selectFile([{ contents: validFile }], { force: true });
        cy.contains('Unknown error occurred in censorship. Please contact a moderator');
        cy.closeElNotifications();
    });

    it('Upload - illegal content', () => {
        cy.intercept('POST', '/api/userprofile/update_avatar', {
            body: {
                type: 'error',
                object: 'censorship',
                category: 'illegal',
            },
        });

        cy.mount(Avatar, mountOptions({
            user: new UserProfile({ left_avatar_n: 1 }),
            isSelf: true,
            expTimeMs: 30000,
        }));

        cy.get('input[type=file]').selectFile([{ contents: validFile }], { force: true });
        cy.contains('The content is blocked by censorship. Please use another file or contact a moderator for manual review');
        cy.closeElNotifications();
    });

    it('Upload - success', () => {
        const user = new UserProfile({ left_avatar_n: 1 });

        cy.intercept('POST', '/api/userprofile/update_avatar', {
            body: {
                type: 'success',
            },
        });

        cy.mount(Avatar, mountOptions({
            user: user,
            isSelf: true,
            expTimeMs: 30000,
        }));

        cy.get('input[type=file]').selectFile([{ contents: validFile }], { force: true });
        cy.get('img').should('have.attr', 'src').and('include', '?v=1');

        cy.then(() => {
            expect(user.left_avatar_n).to.equal(0);
        });
    });
});
