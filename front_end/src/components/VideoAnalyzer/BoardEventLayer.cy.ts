import type { VueWrapper } from '@vue/test-utils';

import BoardEventLayer from './BoardEventLayer.vue';
import { defaultBoardEventSettings } from './boardEvents';
import { defaultCustomEvent } from './customEvents';
import type { PreparedCustomEvent } from './customEvents';
import type { ReplayMouseTraceEvent } from './mouseTrace';

import i18n from '@/i18n';

const definitions = [
    { ...defaultCustomEvent(), key: 'pulse', color: '#e15759', marker: { shape: 'diamond' as const, size: 8, opacity: 0.6 } },
    { ...defaultCustomEvent(), key: 'held', type: 'sustained' as const, line: { style: 'dash' as const, width: 3, opacity: 0.5 } },
];
const mouseEvents: ReplayMouseTraceEvent[] = [
    { row: 1, column: 1, timeMs: 10, eventIndex: 0, action: 'lc', state: 'du' },
    { row: 1, column: 2, timeMs: 10, eventIndex: 1, action: 'mv', state: 'du' },
    { row: 2, column: 2, timeMs: 20, eventIndex: 2, action: 'mv', state: 'du' },
    { row: 3, column: 2, timeMs: 30, eventIndex: 3, action: 'lr', state: 'uu' },
];
const prepared = new Map<string, PreparedCustomEvent>([
    ['pulse', { pulses: [{ timeMs: 10, eventIndex: 1 }, { timeMs: 30, eventIndex: 3, value: 0.25 }], spans: [] }],
    ['held', { pulses: [], spans: [{ startMs: 10, endMs: 30, renderEndMs: 20, startEventIndex: 1, lastEventIndex: 2 }] }],
]);

function mountLayer() {
    cy.mount(BoardEventLayer, { global: { plugins: [i18n] }, props: { definitions, prepared, mouseEvents, settings: { ...defaultBoardEventSettings(), keys: ['pulse', 'held'] }, currentMs: 0, cellSize: 32, rows: 5, columns: 5 } }).then(({ wrapper }) => {
        cy.wrap(wrapper).as('events');
    });
}

describe('<BoardEventLayer />', () => {
    it('renders native points, shared styles and arrows while leaving empty board space transparent to pointers', () => {
        mountLayer();
        cy.get('.board-event-layer').should('have.attr', 'width', '160').and('have.css', 'pointer-events', 'none').and('have.css', 'z-index', '4');
        cy.get('.board-event-layer__pulse').should('have.length', 2).first().should('have.attr', 'transform', 'translate(64, 32)').and('have.attr', 'opacity', '0.6');
        cy.get('.board-event-layer__pulse polygon').should('have.attr', 'points', '0,-4 4,0 0,4 -4,0');
        cy.get('.board-event-layer__path').should('have.attr', 'points', '32,32 64,32 64,64').and('have.attr', 'stroke-dasharray', '6 3').and('have.attr', 'stroke-width', '3');
        cy.get('.board-event-layer__path').parent().should('have.attr', 'opacity', '0.5');
        cy.get('.board-event-layer__arrow').should('have.length', 2);
        cy.get<VueWrapper>('@events').then((wrapper) => wrapper.setProps({ cellSize: 16, definitions: definitions.map((event) => ({ ...event, marker: { ...event.marker, size: 20 } })), settings: { ...defaultBoardEventSettings(), keys: ['pulse', 'held'], arrowShape: 'open' } }));
        cy.get('.board-event-layer').should('have.attr', 'width', '80');
        cy.get('.board-event-layer__pulse polygon').should('have.attr', 'points', '0,-10 10,0 0,10 -10,0');
        cy.get('.board-event-layer__path').should('have.attr', 'points', '16,16 32,16 32,32');
        cy.get('.board-event-layer__arrow').should('have.length', 1).find('path').should('have.attr', 'd', 'M-8,-4 L0,0 L-8,4').and('have.attr', 'fill', 'none');
    });

    it('clips the past by time and event index and synchronizes style changes without showing unselected events', () => {
        mountLayer();
        cy.get<VueWrapper>('@events').then((wrapper) => wrapper.setProps({ currentMs: 10, currentEventIndex: 0, settings: { ...defaultBoardEventSettings(), keys: ['pulse', 'held'], timeRange: 'past' } }));
        cy.get('.board-event-layer__pulse').should('not.exist');
        cy.get('.board-event-layer__path').should('have.attr', 'points', '32,32');
        cy.get('.board-event-layer__arrow').should('not.exist');
        cy.get<VueWrapper>('@events').then((wrapper) => wrapper.setProps({ currentMs: 25, currentEventIndex: 2, definitions: definitions.map((event) => ({ ...event, color: '#123456', line: { ...event.line, style: 'dot' } })) }));
        cy.get('.board-event-layer__pulse').should('have.length', 1).and('have.attr', 'fill', '#123456');
        cy.get('.board-event-layer__path').should('have.attr', 'stroke-dasharray', '1 3');
        cy.get('.board-event-layer__path').parent().should('have.attr', 'stroke', '#123456');
        cy.get<VueWrapper>('@events').then((wrapper) => wrapper.setProps({ settings: defaultBoardEventSettings() }));
        cy.get('.board-event-layer__event').should('not.exist');
    });

    it('shares one Tippy across board pulses and spans and retains full span times when clipped', () => {
        mountLayer();
        let instance: unknown;
        cy.get<SVGSVGElement & { _tippy?: unknown }>('.board-event-layer').then(($svg) => {
            instance = $svg[0]._tippy;
            expect(instance).to.exist;
        });
        cy.get('.board-event-layer__pulse').last().realHover();
        cy.get('.board-event-layer__tooltip:visible').should('have.length', 1).within(() => {
            cy.get('strong').should('have.text', 'pulse');
            cy.get('.event-tooltip__time').should('have.text', 'Time: 0.030 s');
            cy.get('.event-tooltip__value').should('have.text', 'Value: 0.25');
        });
        cy.get<VueWrapper>('@events').then((wrapper) => wrapper.setProps({ currentMs: 10, currentEventIndex: 0, settings: { ...defaultBoardEventSettings(), keys: ['pulse', 'held'], timeRange: 'past' } }));
        cy.get('.board-event-layer__hit-point').should('exist').realHover();
        cy.get('.board-event-layer__tooltip:visible').should('have.length', 1).within(() => {
            cy.get('strong').should('have.text', 'held');
            cy.get('.event-tooltip__start').should('have.text', 'Start: 0.010 s');
            cy.get('.event-tooltip__end').should('have.text', 'End: 0.030 s');
            cy.get('.event-tooltip__duration').should('have.text', 'Duration: 0.020 s');
        });
        cy.get<SVGSVGElement & { _tippy?: unknown }>('.board-event-layer').should(($svg) => {
            expect($svg[0]._tippy).to.eq(instance);
        });
        cy.get<VueWrapper>('@events').then((wrapper) => wrapper.setProps({ currentMs: 25, currentEventIndex: 2 }));
        cy.get('.board-event-layer__tooltip:visible').should('contain.text', 'End: 0.030 s');
        cy.get<VueWrapper>('@events').then((wrapper) => wrapper.setProps({ settings: defaultBoardEventSettings() }));
        cy.get('.board-event-layer__tooltip:visible').should('not.exist');
    });
});
