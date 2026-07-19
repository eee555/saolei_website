import { defineComponent, ref } from 'vue';

import ProgressBar from './ProgressBar.vue';

import i18n from '@/i18n';

function mountProgressBar(current = 0, duration = 1000) {
    const TestHarness = defineComponent({
        components: { ProgressBar },
        expose: [],
        setup() {
            const currentMs = ref(current);
            const durationMs = ref(duration);
            return { currentMs, durationMs };
        },
        template: `
            <div>
                <ProgressBar v-model="currentMs" :duration-ms="durationMs" />
                <span class="progress-bar-test-value">{{ currentMs }}</span>
                <button class="progress-bar-test-shrink-duration" @click="durationMs = 50">shrink</button>
            </div>
        `,
    });

    cy.mount(TestHarness, {
        global: {
            plugins: [i18n],
        },
    });
}

describe('<ProgressBar />', () => {
    it('steps forward and restarts within duration bounds', () => {
        mountProgressBar(950, 1000);

        cy.get('.progress-bar__step').click();
        cy.get('.progress-bar-test-value').should('have.text', '1000');

        cy.get('.progress-bar__restart').click();
        cy.get('.progress-bar-test-value').should('have.text', '0');
    });

    it('clamps current time when duration shrinks', () => {
        mountProgressBar(100, 1000);

        cy.get('.progress-bar-test-shrink-duration').click();

        cy.get('.progress-bar-test-value').should('have.text', '50');
    });

    it('advances current time while playing', () => {
        let animationCallback: FrameRequestCallback | undefined = undefined;
        let testWindow: Window | undefined = undefined;

        cy.window().then((win) => {
            testWindow = win;
            cy.stub(win, 'requestAnimationFrame').callsFake((callback: FrameRequestCallback) => {
                animationCallback = callback;
                return 1;
            });
            cy.stub(win, 'cancelAnimationFrame');
        });
        mountProgressBar(0, 1000);

        cy.get('.progress-bar__play').click();
        cy.then(() => {
            expect(animationCallback).not.to.equal(undefined);
            expect(testWindow).not.to.equal(undefined);
            animationCallback?.((testWindow?.performance.now() ?? 0) + 250);
        });

        cy.get('.progress-bar-test-value').invoke('text').then((value) => {
            expect(Number(value)).to.be.greaterThan(0);
            expect(Number(value)).to.be.lessThan(1000);
        });
    });
});
