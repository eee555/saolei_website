import VideoAbstractDisplay from './VideoAbstractDisplay.vue';

import i18n from '@/i18n';
import { VideoAbstract } from '@/utils/videoabstract';
import { mockVideoInfo } from '@cy/support/videoInfo';

describe('<VideoAbstractDisplay />', () => {
    it('loads missing parsed fields by ID without requesting metadata or inventing an upload date', () => {
        mockVideoInfo([{ id: 42, software: 'a', timems: 12345, bv: 100, cl: 30, ce: 20 }]);
        cy.mount(VideoAbstractDisplay, { props: { id: 42 }, global: { plugins: [i18n] } });
        cy.wait('@parsedVideoInfo').its('request.query.ids').should('eq', '42');
        cy.get('.descriptions').should('contain.text', '12.345').and('contain.text', '100');
        cy.get('.descriptions dd').should('have.length', 9);
        cy.get('@videoMetadata.all').should('have.length', 0);
    });

    it('renders absent or incomplete data without invented dates or non-finite statistics', () => {
        cy.mount(VideoAbstractDisplay, { global: { plugins: [i18n] } });
        cy.get('.descriptions dd').should('have.length', 9).and('have.text', '—————————');
        cy.get('.descriptions').should('not.contain.text', 'NaN').and('not.contain.text', 'Invalid Date');
        cy.get('img').should('not.exist');
        cy.get<ComponentWrapper<typeof VideoAbstractDisplay>>('@vue').then((wrapper) => wrapper.setProps({
            video: { software: 'a', level: 'e', mode: '00', timems: 12345, bv: 100, upload_time: 'invalid', end_time: new Date(NaN) },
        }));
        cy.get('.descriptions dd').should('have.length', 9);
        cy.get('.descriptions').should('contain.text', '12.345').and('contain.text', '100').and('not.contain.text', 'NaN');
        cy.get('img').should('have.length', 1);
        cy.get<ComponentWrapper<typeof VideoAbstractDisplay>>('@vue').then((wrapper) => wrapper.setProps({ video: null }));
        cy.get('.descriptions dd').should('have.length', 9).and('have.text', '—————————');
    });

    it('keeps valid zero statistics and accepts a complete VideoAbstract', () => {
        cy.mount(VideoAbstractDisplay, {
            props: { video: new VideoAbstract({ id: 1, software: 'e', level: 'b', mode: '00', timems: 0, bv: 0, cl: 0, ce: 0, upload_time: '2026-10-22T00:00:00Z', state: 'c' }) },
            global: { plugins: [i18n] },
        });
        cy.get('.descriptions dd').eq(1).should('have.text', '0.000');
        cy.get('.descriptions dd').eq(2).should('have.text', '0');
        cy.get('.descriptions').should('not.contain.text', 'NaN').and('not.contain.text', 'Infinity');
    });
});
