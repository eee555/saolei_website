import { defineComponent, h } from 'vue';

import VideoInfoProgress from './VideoInfoProgress.vue';

import i18n from '@/i18n';
import { serviceConfig } from '@/services/store';
import { fetchVideoInfos } from '@/services/videoInfoService';
import { hashRouter, installHashHistoryCleanup } from '@cy/support/hashHistory';
import { mockVideoInfo } from '@cy/support/videoInfo';

describe('<VideoInfoProgress />', () => {
    installHashHistoryCleanup();

    it('shows missing-item progress across batches and skips the overlay on cache hits', () => {
        serviceConfig.value.videoInfoBatchSize = 1;
        serviceConfig.value.videoInfoBatchDelay = 500;
        const metadata = mockVideoInfo([{ id: 91001 }, { id: 91002 }]);
        const router = hashRouter({ initialPath: '/player/7/videos' });
        cy.mount(defineComponent({
            expose: [],
            render: () => h('div', [
                h('button', { onClick: () => {
                    void fetchVideoInfos(metadata);
                } }, 'Load'),
                h(VideoInfoProgress),
            ]),
        }), { global: { plugins: [i18n, router] } });
        cy.contains('button', 'Load').click();
        cy.get('[role=dialog]').should('be.visible').and('contain.text', '0 / 2');
        cy.wait('@parsedVideoInfo');
        cy.get('[role=dialog]').should('contain.text', '1 / 2');
        cy.wait('@parsedVideoInfo');
        cy.get('[role=dialog]').should('not.exist');
        cy.contains('button', 'Load').click();
        cy.get('[role=dialog]').should('not.exist');
        cy.get('@parsedVideoInfo.all').should('have.length', 2);
    });

    afterEach(() => {
        serviceConfig.value.videoInfoBatchSize = 100;
        serviceConfig.value.videoInfoBatchDelay = 250;
    });
});
