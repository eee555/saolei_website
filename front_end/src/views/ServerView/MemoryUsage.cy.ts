import { memoryColors } from './memory';
import { DonutStub, memoryResponse } from './memory.test-data';
import MemoryUsage from './MemoryUsage.vue';

import i18n from '@/i18n';
import { local } from '@/store';

const global = { plugins: [i18n], stubs: { VueUiDonut: DonutStub } };

describe('Server process memory', () => {
    const originalDark = local.value.darkmode;
    const originalLocale = i18n.global.locale.value;
    afterEach(() => {
        local.value.darkmode = originalDark;
        i18n.global.locale.value = originalLocale;
    });

    it('shows six groups, their share, the process total and separate host memory', () => {
        cy.mount(MemoryUsage, { props: { section: memoryResponse().memory }, global: { plugins: [i18n] } });
        cy.get('.vue-data-ui-legend-item').should('have.length', 6);
        cy.contains('.vue-data-ui-legend-item', 'uWSGI').should('contain.text', '1.00 KB').and('contain.text', '33.3%');
        cy.contains('.vue-data-ui-legend-item', 'db_worker').should('contain.text', '256 B');
        cy.get('.statistics-total').should('contain.text', 'Total: 3.00 KB');
        cy.contains('.memory-description', 'PSS').should('be.visible');
        cy.contains('.memory-description', 'Host memory: 8.00 KB').should('contain.text', 'Available memory: 2.00 KB');
        cy.get('time').should('have.attr', 'datetime', '2026-10-15T12:00:00Z');
        cy.contains('.statistics-cache-note', '5 minutes').should('be.visible');
        cy.contains('button', 'Refresh').click();
        cy.get<ComponentWrapper<typeof MemoryUsage>>('@vue').should((wrapper) => {
            expect(wrapper.emitted('refresh')).to.have.length(1);
        });
    });

    it('keeps the last complete result when a later section is unreadable', () => {
        const section = memoryResponse().memory;
        cy.mount(MemoryUsage, { props: { section }, global });
        cy.get('.statistics-total').should('contain.text', '3.00 KB');
        cy.get<ComponentWrapper<typeof MemoryUsage>>('@vue').then((wrapper) => wrapper.setProps({
            section: { ...section, status: 'unavailable', reason: 'permission_denied', groups: null, total_bytes: null, sampled_at: null, host: null, unreadable_processes: 2 },
        }));
        cy.get('[role="alert"]').should('contain.text', 'Permission').and('contain.text', 'last successful result');
        cy.get('.statistics-total').should('contain.text', '3.00 KB');
        cy.get('time').should('have.attr', 'datetime', section.sampled_at);
    });

    it('distinguishes loading, unreadable memory and a genuine zero result', () => {
        cy.mount(MemoryUsage, { props: { loading: true }, global });
        cy.get('[role="status"]').should('contain.text', 'Loading');
        cy.get('button').should('be.disabled');
        cy.get('.statistics-total').should('not.exist');
        const section = memoryResponse().memory;
        cy.get<ComponentWrapper<typeof MemoryUsage>>('@vue').then((wrapper) => wrapper.setProps({
            loading: false,
            section: { ...section, status: 'unavailable', reason: 'permission_denied', groups: null, total_bytes: null, sampled_at: null },
        }));
        cy.get('[role="alert"]').should('contain.text', 'Permission');
        cy.get('.statistics-total').should('not.exist');
        cy.get<ComponentWrapper<typeof MemoryUsage>>('@vue').then((wrapper) => wrapper.setProps({
            section: { ...section, total_bytes: 0, groups: { uwsgi: 0, apscheduler: 0, redis: 0, mysql: 0, db_worker: 0, other: 0 } },
        }));
        cy.get('[role="alert"]').should('not.exist');
        cy.get('[role="status"]').should('contain.text', 'zero');
        cy.get('.statistics-total').should('contain.text', 'Total: 0 B');
        cy.get('[data-cy="memory-donut"]').should('not.exist');
    });

    it('reacts to theme and language without changing category colors', () => {
        cy.mount(MemoryUsage, { props: { section: memoryResponse().memory }, global });
        cy.then(() => {
            local.value.darkmode = true;
        });
        cy.get('[data-cy="memory-donut"]').should('have.attr', 'data-theme', 'dark');
        cy.then(() => {
            i18n.global.locale.value = 'zh-cn';
        });
        cy.contains('h2', '内存占用').should('be.visible');
        cy.get('[data-cy="memory-donut"]').should(($donut) => {
            const series = JSON.parse($donut.attr('data-series') ?? '[]') as { name: string; color: string; values: number[] }[];
            expect(series[5].name).to.equal('其他');
            expect(series.map((item) => item.color)).to.deep.equal(memoryColors);
            expect(series.map((item) => item.values[0])).to.deep.equal([1024, 512, 256, 512, 256, 512]);
        });
        cy.then(() => {
            local.value.darkmode = false;
        });
        cy.get('[data-cy="memory-donut"]').should('have.attr', 'data-theme', '');
    });
});
