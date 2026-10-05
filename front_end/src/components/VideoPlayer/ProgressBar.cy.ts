import ProgressBar from './ProgressBar.vue';

import i18n from '@/i18n';

function mountProgressBar(current = 0, duration = 1000) {
    cy.mount(ProgressBar, {
        props: {
            modelValue: current,
            durationMs: duration,
        },
        global: {
            plugins: [i18n],
        },
    }).then(({ wrapper }) => {
        return wrapper.setProps({
            'onUpdate:modelValue': (value: number) => {
                void wrapper.setProps({ modelValue: value });
            },
        });
    });
}

function modelUpdate(index: number) {
    return cy.get('@vue').then((wrapper: ComponentWrapper<typeof ProgressBar>) => {
        return wrapper.emitted('update:modelValue')?.[index]?.[0];
    });
}

function lastModelUpdate() {
    return cy.get('@vue').then((wrapper: ComponentWrapper<typeof ProgressBar>) => {
        const events = wrapper.emitted('update:modelValue') ?? [];
        return events.at(-1)?.[0];
    });
}

describe('<ProgressBar />', () => {
    it('emits bounded step and restart updates', () => {
        mountProgressBar(950, 1000);

        cy.get('button[aria-label="Step 0.1 seconds"]').focus();
        cy.realPress('Enter');
        modelUpdate(0).should('eq', 1000);

        cy.get('button[aria-label="Restart"]').focus();
        cy.realPress('Space');
        modelUpdate(1).should('eq', 0);
    });

    it('emits a clamped update when duration shrinks', () => {
        mountProgressBar(100, 1000);

        cy.get('@vue').then((wrapper: ComponentWrapper<typeof ProgressBar>) => {
            return wrapper.setProps({ durationMs: 50 });
        });

        modelUpdate(0).should('eq', 50);
    });

    it('emits current time updates while playing', () => {
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

        cy.get('.progress-bar .pi-play').closest('button').click();
        cy.then(() => {
            expect(animationCallback).not.to.equal(undefined);
            expect(testWindow).not.to.equal(undefined);
            animationCallback?.((testWindow?.performance.now() ?? 0) + 250);
        });

        lastModelUpdate().then((value) => {
            expect(Number(value)).to.be.greaterThan(0);
            expect(Number(value)).to.be.lessThan(1000);
        });
    });

    for (const { playing, fraction, expected, fromTrack } of [
        { playing: true, fraction: 0.75, expected: 850, fromTrack: false },
        { playing: false, fraction: 0.75, expected: 750, fromTrack: false },
        { playing: true, fraction: 1, expected: 1000, fromTrack: false },
        { playing: true, fraction: 0.75, expected: 850, fromTrack: true },
    ]) {
        it(`drags the ${fromTrack ? 'track' : 'handle'} to ${fraction * 100}% while ${playing ? 'playing' : 'paused'} and ${expected === 850 ? 'continues playback' : 'stays paused'}`, () => {
            let animationCallback: FrameRequestCallback | undefined;
            let targetX = 0;
            let targetY = 0;

            cy.window().then((win) => {
                cy.stub(win.performance, 'now').returns(1000);
                cy.stub(win, 'requestAnimationFrame').callsFake((callback: FrameRequestCallback) => {
                    animationCallback = callback;
                    return 1;
                });
                cy.stub(win, 'cancelAnimationFrame');
            });
            mountProgressBar(0, 1000);
            if (playing) {
                cy.get('.progress-bar .pi-play').closest('button').click();
                cy.then(() => animationCallback?.(1100));
                lastModelUpdate().should('eq', 100);
            }

            cy.get('.progress-bar__slider .el-slider__runway').then(($runway) => {
                const bounds = $runway[0].getBoundingClientRect();
                targetX = bounds.left + bounds.width * fraction;
                targetY = bounds.top + bounds.height / 2;
            });
            cy.get(`.progress-bar__slider .${fromTrack ? 'el-slider__runway' : 'el-slider__button-wrapper'}`).then(($handle) => {
                const bounds = $handle[0].getBoundingClientRect();
                const position = { button: 0, clientX: bounds.left + bounds.width * (fromTrack ? 0.25 : 0.5), clientY: targetY };
                cy.wrap($handle).trigger('pointerdown', { ...position, eventConstructor: 'PointerEvent' });
                cy.wrap($handle).trigger('mousedown', position);
            });
            if (playing) {
                cy.then(() => animationCallback?.(2000));
                lastModelUpdate().should('eq', fromTrack ? 250 : 100);
            }
            cy.get('body').then(($body) => {
                cy.wrap($body).trigger('mousemove', { clientX: targetX, clientY: targetY });
            });
            lastModelUpdate().should('eq', fraction * 1000);
            if (playing) {
                cy.then(() => animationCallback?.(3000));
                lastModelUpdate().should('eq', fraction * 1000);
            }
            cy.get('body').trigger('mouseup');
            cy.get(`.progress-bar .${expected === 850 ? 'pi-pause' : 'pi-play'}`).should('exist');
            cy.get('@vue').should((wrapper: ComponentWrapper<typeof ProgressBar>) => {
                const slider = wrapper.findComponent({ name: 'ElSlider' });
                expect(slider.emitted('change')).to.have.length(1);
            });
            cy.then(() => animationCallback?.(1100));
            lastModelUpdate().should('eq', expected);
        });
    }
});
