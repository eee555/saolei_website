import { defineComponent, h } from 'vue';

import ReplayControls from './ReplayControls.vue';

import { usePlayback } from '@/components/VideoAnalyzer/usePlayback';
import i18n from '@/i18n';

const Host = defineComponent({
    expose: [],
    setup() {
        const playback = usePlayback(1000);
        return () => h(ReplayControls, { playback, positionMs: playback.currentMs.value });
    },
});

describe('minigame replay controls', () => {
    let advance: (ms: number) => void;
    beforeEach(() => {
        cy.window().then((win) => {
            let now = 0;
            let frame: FrameRequestCallback | undefined;
            cy.stub(win.performance, 'now').callsFake(() => now);
            cy.stub(win, 'requestAnimationFrame').callsFake((callback: FrameRequestCallback) => {
                frame = callback;
                return 1;
            });
            cy.stub(win, 'cancelAnimationFrame').callsFake(() => {
                frame = undefined;
            });
            advance = (ms) => {
                now += ms;
                const callback = frame;
                frame = undefined;
                callback?.(now);
            };
        });
        cy.mount(Host, { global: { plugins: [i18n] } });
        cy.get('[data-cy="minigame-replay-play"]').should('have.attr', 'aria-label', 'Play').find('.pi-play').should('exist');
    });
    afterEach(() => {
        cy.window().trigger('pointerup', { eventConstructor: 'PointerEvent' });
    });

    it('preserves paused and playing states across drags, including release outside the slider', () => {
        cy.get('[data-cy="minigame-replay-position"]').trigger('pointerdown', { eventConstructor: 'PointerEvent', button: 0 });
        cy.get('[data-cy="minigame-replay-position"]').invoke('val', '300').trigger('input');
        cy.window().trigger('pointerup', { eventConstructor: 'PointerEvent' });
        cy.then(() => {
            advance(100);
        });
        cy.get('[data-cy="minigame-replay-position"]').should('have.value', '300');
        cy.get('[data-cy="minigame-replay-play"]').should('have.attr', 'aria-pressed', 'false').click();
        cy.then(() => {
            advance(200);
        });
        cy.get('[data-cy="minigame-replay-position"]').should('have.value', '500');
        cy.get('[data-cy="minigame-replay-position"]').trigger('pointerdown', { eventConstructor: 'PointerEvent', button: 0 });
        cy.get('[data-cy="minigame-replay-position"]').invoke('val', '100').trigger('input');
        cy.then(() => {
            advance(200);
        });
        cy.get('[data-cy="minigame-replay-position"]').should('have.value', '100');
        cy.window().trigger('pointerup', { eventConstructor: 'PointerEvent' });
        cy.then(() => {
            advance(200);
        });
        cy.get('[data-cy="minigame-replay-position"]').should('have.value', '300');
        cy.get('[data-cy="minigame-replay-play"]').should('have.attr', 'aria-pressed', 'true').and('have.attr', 'aria-label', 'Pause').find('.pi-pause').should('exist');
    });

    it('stops at the end during playback or seeking, and can play again from the beginning', () => {
        cy.get('[data-cy="minigame-replay-play"]').click();
        cy.then(() => {
            advance(1200);
        });
        cy.get('[data-cy="minigame-replay-position"]').should('have.value', '1000');
        cy.get('[data-cy="minigame-replay-play"]').should('have.attr', 'aria-pressed', 'false').click();
        cy.then(() => {
            advance(100);
        });
        cy.get('[data-cy="minigame-replay-position"]').should('have.value', '100');
        cy.get('[data-cy="minigame-replay-position"]').trigger('pointerdown', { eventConstructor: 'PointerEvent', button: 0 });
        cy.get('[data-cy="minigame-replay-position"]').invoke('val', '1000').trigger('input');
        cy.get('[data-cy="minigame-replay-position"]').trigger('change');
        cy.get('[data-cy="minigame-replay-play"]').should('have.attr', 'aria-pressed', 'false');
    });
});
