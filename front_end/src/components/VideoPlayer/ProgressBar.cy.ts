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

        cy.get('.progress-bar__step').click();
        modelUpdate(0).should('eq', 1000);

        cy.get('.progress-bar__restart').click();
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

        cy.get('.progress-bar__play').click();
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
});
