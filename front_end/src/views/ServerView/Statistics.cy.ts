import DiskUsage from './DiskUsage.vue';
import TaskSummary from './TaskSummary.vue';
import VideoSummary from './VideoSummary.vue';

import $axios from '@/http';
import i18n from '@/i18n';

const global = {
    plugins: [i18n],
    config: { globalProperties: { $axios } },
};
const disk = { total: 8192, used: 6144, free: 2048, video: 3072, db: 1024 };
const tasks = { total: 1000, status: { READY: 100, RUNNING: 100, SUCCESSFUL: 700, FAILED: 100 } };
const videos = {
    total: 1000,
    software: { a: 100, e: 200, m: 300, r: 400 },
    level: { b: 200, i: 200, e: 200, c8_8_40: 400 },
    mode: { '00': 500, '01': 0, '04': 0, '05': 100, '07': 100, '08': 100, '09': 100, 10: 100, 11: 0 },
    state: { a: 100, b: 100, c: 700, d: 100, e: 0 },
};

describe('Server statistics cards', () => {
    const originalLocale = i18n.global.locale.value;
    afterEach(() => {
        i18n.global.locale.value = originalLocale;
    });

    it('uses the same donut layout for disk space and counts free space only once', () => {
        cy.intercept('GET', '**/api/monitor/diskusage', { body: disk }).as('disk');
        cy.mount(DiskUsage, { global });
        cy.wait('@disk');
        cy.get('.vue-data-ui-legend-item').should('have.length', 4);
        cy.contains('.vue-data-ui-legend-item', 'Videos').should('contain.text', '3.00 KB').and('contain.text', '37.5%');
        cy.contains('.vue-data-ui-legend-item', 'Database').should('contain.text', '1.00 KB').and('contain.text', '12.5%');
        cy.contains('.vue-data-ui-legend-item', 'Other').should('contain.text', '2.00 KB').invoke('text').should('match', /25(?:\.0)?%/);
        cy.contains('.vue-data-ui-legend-item', 'Free').should('contain.text', '2.00 KB').invoke('text').should('match', /25(?:\.0)?%/);
        cy.get('.statistics-total').should('contain.text', 'Total: 8.00 KB');
    });

    it('handles an empty video database and rejects overlapping disk categories', () => {
        cy.intercept('GET', '**/api/monitor/diskusage', { body: { ...disk, video: null, db: null } }).as('disk');
        cy.mount(DiskUsage, { global });
        cy.wait('@disk');
        cy.contains('.vue-data-ui-legend-item', 'Videos').should('contain.text', '0 B');
        cy.contains('.vue-data-ui-legend-item', 'Other').should('contain.text', '6.00 KB');
        cy.intercept('GET', '**/api/monitor/diskusage', { body: { ...disk, video: disk.total } }).as('invalidDisk');
        cy.contains('button', 'Refresh').click();
        cy.wait('@invalidDisk');
        cy.get('[role="alert"]').should('contain.text', 'last successful result');
        cy.contains('.vue-data-ui-legend-item', 'Other').should('contain.text', '6.00 KB');
        cy.contains('button', 'Refresh').should('not.be.disabled');
    });

    it('shows task counts without byte units and updates translated status labels', () => {
        cy.intercept('GET', '**/api/monitor/tasksummary', { body: tasks }).as('tasks');
        cy.mount(TaskSummary, { global });
        cy.wait('@tasks');
        cy.get('.statistics-total').should('contain.text', 'Total: 1,000').and('not.contain.text', 'KB');
        cy.contains('.vue-data-ui-legend-item', 'Successful').should('contain.text', '700').invoke('text').should('match', /70(?:\.0)?%/);
        cy.then(() => {
            i18n.global.locale.value = 'zh-cn';
        });
        cy.contains('h2', '后台任务').should('be.visible');
        cy.contains('.vue-data-ui-legend-item', '已完成').should('be.visible');
        cy.contains('.vue-data-ui-legend-item', '失败').should('be.visible');
    });

    it('shows an explicit zero task total and retains it after a failed refresh', () => {
        cy.intercept('GET', '**/api/monitor/tasksummary', { body: { total: 0, status: { READY: 0, RUNNING: 0, SUCCESSFUL: 0, FAILED: 0 } } }).as('tasks');
        cy.mount(TaskSummary, { global });
        cy.wait('@tasks');
        cy.get('[role="status"]').should('contain.text', 'zero');
        cy.get('.statistics-total').should('contain.text', 'Total: 0');
        cy.get('.vue-ui-donut').should('not.exist');
        cy.intercept('GET', '**/api/monitor/tasksummary', { statusCode: 500 }).as('failedTasks');
        cy.contains('button', 'Refresh').click();
        cy.wait('@failedTasks');
        cy.get('[role="alert"]').should('contain.text', 'last successful result');
        cy.get('.statistics-total').should('contain.text', 'Total: 0');
        cy.get('[data-statistic="tasks"]').should('have.attr', 'aria-busy', 'false');
    });

    it('shows all video dimensions and omits unsupported modes and verification states', () => {
        cy.intercept('GET', '**/api/monitor/videosummary', { body: videos }).as('videos');
        cy.mount(VideoSummary, { global });
        cy.wait('@videos');
        cy.get('.statistics-total').should('contain.text', 'Total: 1,000');
        const activeLegend = '.video-panel[aria-hidden="false"] .vue-data-ui-legend-item';
        cy.get(activeLegend).should('have.length', 4);
        cy.get(activeLegend).first().should('contain.text', '100');
        cy.contains('.video-dimensions button', 'Level').click();
        cy.contains('.video-dimensions button', 'Level').should('have.attr', 'aria-pressed', 'true');
        cy.contains(activeLegend, '8x8/40').should('contain.text', '400').invoke('text').should('match', /40(?:\.0)?%/);
        cy.contains('.video-dimensions button', 'Mode').click();
        cy.get(activeLegend).should('have.length', 7).and('not.contain.text', 'UPK').and('not.contain.text', 'Win7').and('not.contain.text', 'Recursive');
        cy.contains(activeLegend, 'Strong Guessing').should('be.visible');
        cy.contains('.video-dimensions button', 'State').click();
        cy.get(activeLegend).should('have.length', 4);
        cy.contains(activeLegend, '700').should('be.visible');
        cy.get('@videos.all').should('have.length', 1);
    });

    it('keeps video card height stable across dimensions at different widths and languages', () => {
        cy.intercept('GET', '**/api/monitor/videosummary', { body: videos }).as('videos');
        cy.mount(VideoSummary, { global });
        cy.wait('@videos');
        cy.get('.video-panel').should('have.length', 4);
        cy.get('.video-panel .vue-data-ui-legend').should('have.length', 4);

        for (const language of ['en', 'zh-cn'] as const) {
            cy.then(() => {
                i18n.global.locale.value = language;
            });
            cy.get('h2').should('contain.text', language === 'en' ? 'Video Statistics' : '录像统计');
            cy.contains('.video-panel[data-dimension="mode"] .vue-data-ui-legend-item', language === 'en' ? 'Strong Guessing' : '强可猜').should('exist');
            for (const width of [420, 260]) {
                cy.get('[data-statistic="videos"]').invoke('css', 'width', `${width}px`);
                cy.get('.video-panel[data-dimension="mode"] .vue-data-ui-legend-item').should('have.length', 7);
                cy.get('[data-statistic="videos"]').then(($card) => {
                    const { height } = $card[0].getBoundingClientRect();
                    for (const index of [0, 1, 2, 3, 0]) {
                        cy.get('.video-dimensions button').eq(index).click();
                        cy.get('.video-dimensions button').eq(index).should('have.attr', 'aria-pressed', 'true');
                        cy.get('.video-panel[aria-hidden="false"]').should('have.length', 1).and('be.visible').and('not.have.attr', 'inert');
                        cy.get('.video-panel[aria-hidden="true"]').should('have.length', 3).each(($panel) => {
                            expect($panel).to.have.css('visibility', 'hidden');
                            expect($panel).to.have.attr('inert');
                        });
                        cy.get('[data-statistic="videos"]').should(($current) => {
                            expect($current[0].getBoundingClientRect().height).to.be.closeTo(height, 0.5);
                        });
                    }
                });
            }
        }
        cy.get('@videos.all').should('have.length', 1);
    });

    it('finishes the initial loading state after an error and retries from the card', () => {
        cy.intercept('GET', '**/api/monitor/videosummary', { statusCode: 503 }).as('failedVideos');
        cy.mount(VideoSummary, { global });
        cy.wait('@failedVideos');
        cy.get('[role="alert"]').should('contain.text', 'Could not load');
        cy.get('.statistics-total').should('not.exist');
        cy.get('[data-statistic="videos"]').should('have.attr', 'aria-busy', 'false');
        cy.intercept('GET', '**/api/monitor/videosummary', { body: videos }).as('videos');
        cy.contains('button', 'Refresh').click();
        cy.wait('@videos');
        cy.get('[role="alert"]').should('not.exist');
        cy.get('.statistics-total').should('contain.text', 'Total: 1,000');
    });
});
