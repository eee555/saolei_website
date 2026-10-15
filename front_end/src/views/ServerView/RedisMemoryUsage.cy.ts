import { DonutStub, memoryResponse } from './memory.test-data';
import RedisMemoryUsage from './RedisMemoryUsage.vue';

import i18n from '@/i18n';

const global = { plugins: [i18n], stubs: { VueUiDonut: DonutStub } };

describe('Redis memory distribution', () => {
    it('renders the real donut and all four categories with allocator totals', () => {
        cy.mount(RedisMemoryUsage, { props: { section: memoryResponse().redis }, global: { plugins: [i18n] } });
        cy.get('[data-memory-chart="redis"] svg').should('exist');
        cy.get('.vue-data-ui-legend-item').should('have.length', 4);
        cy.contains('.vue-data-ui-legend-item', 'PB rankings').should('contain.text', '512 B');
        cy.contains('.vue-data-ui-legend-item', 'PB rankings').invoke('text').should('match', /50(?:\.0)?%/);
        cy.contains('.vue-data-ui-legend-item', 'Other rankings').should('contain.text', '256 B');
        cy.contains('.vue-data-ui-legend-item', 'Latest videos').should('contain.text', '128 B');
        cy.contains('.vue-data-ui-legend-item', /^Other:/).should('contain.text', '128 B');
        cy.get('.statistics-total').should('contain.text', 'Total: 1.00 KB');
        cy.contains('.memory-description', 'estimated').should('have.attr', 'title').and('contain', 'other databases');
        cy.contains('.vue-data-ui-legend-item', 'PB rankings').focus();
        cy.contains('.vue-data-ui-legend-item', 'PB rankings').trigger('keydown', { key: 'Enter' });
        cy.contains('.vue-data-ui-legend-item', 'PB rankings').find('svg').should('have.css', 'opacity', '0.5');
    });

    it('does not turn unavailable metadata into zero memory', () => {
        cy.mount(RedisMemoryUsage, {
            props: { section: { ...memoryResponse().redis, status: 'unavailable', reason: 'metadata_unavailable', sampled_at: null, total_bytes: null, groups: null } }, global,
        });
        cy.get('[role="alert"]').should('contain.text', 'PB cache index');
        cy.get('.statistics-total').should('not.exist');
        cy.get('.vue-data-ui-legend').should('not.exist');
    });

    it('keeps successful data on a failed refresh and publishes a later complete sample', () => {
        const section = memoryResponse().redis;
        cy.mount(RedisMemoryUsage, { props: { section }, global });
        cy.get<ComponentWrapper<typeof RedisMemoryUsage>>('@vue').then((wrapper) => wrapper.setProps({ failed: true }));
        cy.get('[role="alert"]').should('contain.text', 'Could not load').and('contain.text', 'last successful result');
        cy.get('.statistics-total').should('contain.text', '1.00 KB');
        cy.get<ComponentWrapper<typeof RedisMemoryUsage>>('@vue').then((wrapper) => wrapper.setProps({
            failed: false, section: { ...section, sampled_at: '2026-10-15T12:05:01Z', total_bytes: 2048, groups: { pb_rankings: 1024, other_rankings: 512, latest_videos: 256, other: 256 } },
        }));
        cy.get('[role="alert"]').should('not.exist');
        cy.get('.statistics-total').should('contain.text', '2.00 KB');
        cy.get('time').should('have.attr', 'datetime', '2026-10-15T12:05:01Z');
    });
});
