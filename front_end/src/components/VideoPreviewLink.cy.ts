import { defineComponent, h } from 'vue';

import VideoPreviewLink from './VideoPreviewLink.vue';

import { videoplayerstore } from '@/store';
import type { MS_Software } from '@/utils/ms_const';

function mountLink(id: number | null | undefined, software?: MS_Software) {
    cy.mount(defineComponent({
        expose: [],
        render: () => h(VideoPreviewLink, { id, software }, () => '12.345'),
    }));
}

describe('<VideoPreviewLink />', () => {
    beforeEach(() => {
        videoplayerstore.visible = false;
    });

    afterEach(() => {
        videoplayerstore.visible = false;
    });

    it('opens the existing player by keyboard without navigating away', () => {
        cy.intercept('GET', '**/video/get_software/*', { body: { msg: 'e' } }).as('software');
        mountLink(42);

        cy.get('.video-preview-link').should('have.attr', 'href', '#/video/42').focus();
        cy.realPress('Enter');
        cy.wait('@software').its('request.query.id').should('eq', '42');
        cy.wrap(videoplayerstore).its('visible').should('eq', true);
        cy.wrap(videoplayerstore).its('id').should('eq', 42);
        cy.wrap(videoplayerstore).its('url').should('include', '/api/video/preview?id=42');
        cy.location('hash').should('not.eq', '#/video/42');
        cy.get('@software.all').should('have.length', 1);
    });

    it('opens the preview once on an ordinary click and keeps the supplied software', () => {
        cy.intercept('GET', '**/video/get_software/*', { body: { msg: 'e' } }).as('software');
        mountLink(43, 'r');
        const parentClick = cy.spy().as('parentClick');
        cy.get('.video-preview-link').then(($link) => {
            $link[0].parentElement?.addEventListener('click', () => {
                parentClick();
            });
        }).click();

        cy.wrap(videoplayerstore).its('visible').should('eq', true);
        cy.wrap(videoplayerstore).its('url').should('include', '/api/video/preview?id=43.rmv');
        cy.location('hash').should('not.eq', '#/video/43');
        cy.get('@software.all').should('have.length', 0);
        cy.get('@parentClick').should('not.have.been.called');
    });

    for (const options of [{ ctrlKey: true }, { metaKey: true }, { shiftKey: true }, { altKey: true }, { button: 1 }]) {
        it(`preserves native navigation for ${JSON.stringify(options)} without opening the preview`, () => {
            mountLink(42, 'e');
            const parentClick = cy.spy().as('parentClick');
            cy.get('.video-preview-link').then(($link) => {
                const [link] = $link;
                const handleParentClick = () => {
                    parentClick();
                };
                link.parentElement?.addEventListener('click', handleParentClick);
                link.parentElement?.addEventListener('auxclick', handleParentClick);
                // Observe the component's handling, then prevent browser navigation in this test.
                link.addEventListener(options.button === 1 ? 'auxclick' : 'click', (event) => {
                    expect(event.defaultPrevented).to.equal(false);
                    event.preventDefault();
                }, { once: true });
                link.dispatchEvent(new MouseEvent(options.button === 1 ? 'auxclick' : 'click', { bubbles: true, cancelable: true, ...options }));
            });
            cy.wrap(videoplayerstore).its('visible').should('eq', false);
            cy.get('@parentClick').should('not.have.been.called');
        });
    }

    for (const id of [undefined, null, 0, -1]) {
        it(`renders a non-interactive placeholder for ID ${id}`, () => {
            mountLink(id);
            cy.contains('span', '--').should('be.visible');
            cy.get('.video-preview-link').should('not.exist');
            cy.wrap(videoplayerstore).its('visible').should('eq', false);
        });
    }
});
