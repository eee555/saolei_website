import PBBVButton from './PBBVButton.vue';

import i18n from '@/i18n';
import type { PBCounts } from '@/services/pbRankingService';

describe('<PBBVButton />', () => {
    it('renders the count grid with a fixed header and emits a selected BV before closing', () => {
        const counts: PBCounts = {};
        for (let bv = 1; bv <= 381; bv++) {
            if (bv === 2 || (bv >= 10 && bv <= 19)) continue;
            counts[`std:e:${bv}`] = 7;
        }
        const onSelect = cy.spy().as('select');
        cy.mount(PBBVButton, {
            props: { level: 'e', selectedLevel: 'e', selectedBv: 207, nf: false, counts, onSelect },
            global: { plugins: [i18n] },
        });
        cy.get('.pb-level-button').should('have.attr', 'aria-pressed', 'true').and('have.attr', 'aria-expanded', 'false');
        cy.get('.pb-level-button span').should('have.text', '207');
        cy.get('.pb-level-button').click();
        cy.get('.pb-level-button').should('have.attr', 'aria-expanded', 'true');
        cy.get('.pb-bv-grid').filter(':visible').within(() => {
            cy.get('.pb-bv-header').children().should(($cells) => {
                expect(Array.from($cells).slice(1).map((cell) => cell.textContent)).to.deep.equal(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']);
            });
            cy.get('.pb-bv-header').should(($header) => {
                expect(getComputedStyle($header[0]).gridTemplateColumns.split(' ')).to.have.length(11);
            });
            cy.get('.pb-bv-body .pb-bv-header').should('not.exist');
            cy.get('[data-tens="1"]').should('not.exist');
            cy.get('[data-tens="20"] .pb-bv-label').should('have.text', '20');
            cy.get('[data-bv="0"], [data-bv="382"]').should('not.exist');
            cy.get('[data-bv="1"]').should('have.text', '7').and('not.be.disabled');
            cy.get('[data-bv="2"]').should('have.text', '0').and('be.disabled');
            cy.get('[data-bv="207"]').should('have.attr', 'aria-pressed', 'true');
            cy.get('.pb-bv-body').scrollTo('bottom');
            cy.get('.pb-bv-header').should('be.visible');
            cy.get('[data-bv="381"]').click();
        });
        cy.get('@select').should('have.been.calledOnceWithExactly', 381);
        cy.get('.pb-level-button').should('have.attr', 'aria-expanded', 'false');
    });

    it('reacts to selection, NF, count and level changes, including empty buckets', () => {
        const counts: PBCounts = { 'std:b:1': 11, 'std:b:54': 3, 'std:b:55': 5, 'std:i:216': 4, 'std:i:217': 9, 'nf:b:20': 6 };
        cy.mount(PBBVButton, {
            props: { level: 'b', selectedLevel: 'i', selectedBv: 54, nf: false, counts },
            global: { plugins: [i18n] },
        });
        cy.get('.pb-level-button').should('have.attr', 'aria-pressed', 'false');
        cy.get('.pb-level-button span').should('not.exist');
        cy.get('.pb-level-button').click();
        cy.get('.pb-bv-grid').filter(':visible').find('[data-bv="1"]').should('have.text', '11');
        cy.get('.pb-bv-grid').filter(':visible').find('[data-bv="54"]').should('have.text', '3');
        cy.get('.pb-bv-grid').filter(':visible').find('[data-bv="55"]').should('not.exist');

        cy.get<ComponentWrapper<typeof PBBVButton>>('@vue').then((wrapper) => wrapper.setProps({ selectedLevel: 'b' }));
        cy.get('.pb-level-button span').should('have.text', '54');
        cy.get('.pb-bv-grid').filter(':visible').find('[data-bv="54"]').should('have.attr', 'aria-pressed', 'true');

        cy.get<ComponentWrapper<typeof PBBVButton>>('@vue').then((wrapper) => wrapper.setProps({ nf: true }));
        cy.get('.pb-bv-grid').filter(':visible').within(() => {
            cy.get('.pb-bv-row').should('have.length', 1).and('have.attr', 'data-tens', '2');
            cy.get('[data-bv="20"]').should('have.text', '6').and('not.be.disabled');
            cy.get('[data-bv="21"]').should('have.text', '0').and('be.disabled');
        });

        cy.get<ComponentWrapper<typeof PBBVButton>>('@vue').then((wrapper) => wrapper.setProps({ counts: { ...counts, 'nf:b:20': 0, 'nf:b:30': 8 } }));
        cy.get('.pb-bv-grid').filter(':visible').find('[data-tens="2"]').should('not.exist');
        cy.get('.pb-bv-grid').filter(':visible').find('[data-bv="30"]').should('have.text', '8');

        cy.get<ComponentWrapper<typeof PBBVButton>>('@vue').then((wrapper) => wrapper.setProps({ level: 'i', nf: false }));
        cy.get('.pb-level-button').should('have.attr', 'data-level', 'i').and('have.attr', 'aria-pressed', 'false');
        cy.get('.pb-bv-grid').filter(':visible').find('[data-bv="216"]').should('have.text', '4');
        cy.get('.pb-bv-grid').filter(':visible').find('[data-bv="217"]').should('not.exist');

        cy.get<ComponentWrapper<typeof PBBVButton>>('@vue').then((wrapper) => wrapper.setProps({ counts: {} }));
        cy.get('.pb-bv-grid').filter(':visible').find('.pb-bv-row').should('not.exist');
        cy.get('.pb-bv-grid').filter(':visible').find('.pb-bv-header').should('be.visible');
        cy.get('.pb-bv-grid').filter(':visible').trigger('keydown', { key: 'Escape' });
        cy.get('.pb-level-button').should('have.attr', 'aria-expanded', 'false');
    });
});
