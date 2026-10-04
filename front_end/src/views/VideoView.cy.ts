import VideoView from './VideoView.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { videofilter } from '@/store';
import { pinia } from '@/store/create';

describe('<VideoView />', () => {
    it('toggles the NF switch and resets pagination when the filter changes', () => {
        videofilter.value.pagesize = 20;
        cy.intercept({ method: 'GET', pathname: '/api/video/query' }, {
            body: { count: 21, videos: [] },
        }).as('videos');
        cy.mount(VideoView, { global: { plugins: [i18n, pinia], config: { globalProperties: { $axios } } } });

        cy.wait('@videos').its('request.query').should('include', { nf: 'false', page: '1' });
        cy.get('[role="switch"]').should('have.attr', 'aria-checked', 'false');
        cy.get('.el-pagination .btn-next').click();
        cy.wait('@videos').its('request.query').should('include', { nf: 'false', page: '2' });

        cy.get('.el-switch').click();
        cy.wait('@videos').its('request.query').should('include', { nf: 'true', page: '1' });
        cy.get('[role="switch"]').should('have.attr', 'aria-checked', 'true');
        cy.get('.el-pagination .btn-next').click();
        cy.wait('@videos').its('request.query').should('include', { nf: 'true', page: '2' });

        cy.get('.el-switch').click();
        cy.wait('@videos').its('request.query').should('include', { nf: 'false', page: '1' });
        cy.get('[role="switch"]').should('have.attr', 'aria-checked', 'false');
    });
});
