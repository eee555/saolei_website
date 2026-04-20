import Progress from './Progress.vue';

import i18n from '@/i18n';

function mountOptions(props: any) {
    return {
        props: props,
        global: {
            plugins: [i18n],
        },
    };
}

describe('Progress Component', () => {
    it('renders nothing when all progress is complete', () => {
        cy.mount(Progress, mountOptions({
            parserProgress: { total: 5, parsed: 5 },
            uploadProgress: { total: 10, uploaded: 10, failed: 0 },
        }));
        cy.contains('Parsing files').should('not.exist');
        cy.contains('Uploading').should('not.exist');
    });

    it('renders only parsing progress when parsing incomplete and upload complete', () => {
        cy.mount(Progress, mountOptions({
            parserProgress: { total: 5, parsed: 3 },
            uploadProgress: { total: 10, uploaded: 10, failed: 0 },
        }));
        cy.contains('Parsing files: 3 / 5').should('be.visible');
        cy.contains('Uploading').should('not.exist');
    });

    it('renders only uploading progress when parsing complete and upload incomplete', () => {
        cy.mount(Progress, mountOptions({
            parserProgress: { total: 5, parsed: 5 },
            uploadProgress: { total: 10, uploaded: 7, failed: 2 },
        }));
        // uploaded + failed = 9
        cy.contains('Uploading: 9 / 10').should('be.visible');
        cy.contains('Parsing files').should('not.exist');
    });

    it('renders both progress bars when both are incomplete', () => {
        cy.mount(Progress, mountOptions({
            parserProgress: { total: 5, parsed: 2 },
            uploadProgress: { total: 10, uploaded: 5, failed: 1 },
        }));
        cy.contains('Parsing files: 2 / 5').should('be.visible');
        cy.contains('Uploading: 6 / 10').should('be.visible');
    });

    it('updates correctly when props change', () => {
        cy.mount(Progress, mountOptions({
            parserProgress: { total: 5, parsed: 2 },
            uploadProgress: { total: 10, uploaded: 5, failed: 0 },
        }));
        cy.contains('Parsing files: 2 / 5').should('be.visible');
        cy.contains('Uploading: 5 / 10').should('be.visible');

        // Update props to complete state
        cy.get('@vue').then((wrapper: any) => {
            wrapper.setProps({
                parserProgress: { total: 5, parsed: 5 },
                uploadProgress: { total: 10, uploaded: 10, failed: 0 },
            });
        });
        cy.contains('Parsing files').should('not.exist');
        cy.contains('Uploading').should('not.exist');
    });

    it('handles zero totals gracefully', () => {
        cy.mount(Progress, mountOptions({
            parserProgress: { total: 0, parsed: 0 },
            uploadProgress: { total: 0, uploaded: 0, failed: 0 },
        }));
        cy.contains('Parsing files').should('not.exist');
        cy.contains('Uploading').should('not.exist');
    });

    it('handles partial failures in upload progress', () => {
        cy.mount(Progress, mountOptions({
            parserProgress: { total: 3, parsed: 3 },
            uploadProgress: { total: 5, uploaded: 2, failed: 2 },
        }));
        // Still incomplete because 2+2 = 4 < 5
        cy.contains('Uploading: 4 / 5').should('be.visible');
    });
});
