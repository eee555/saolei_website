import { describe, expect, it } from 'vitest';

import { ClassicMouseAutomaton } from './classicMouse';
import type { ClassicMouseAction, ClassicMouseEvent, ClassicMouseState } from './classicMouse';

interface Sequence {
    name: string;
    events: ClassicMouseEvent[];
    actions: (ClassicMouseAction | null)[];
    state: ClassicMouseState;
}

const sequences: Sequence[] = [
    { name: 'triggers left only on release', events: ['lc', 'lr'], actions: [null, 'left'], state: 'idle' },
    { name: 'triggers right only on press', events: ['rc', 'rr'], actions: ['right', null], state: 'idle' },
    { name: 'left-first chord triggers on left release only', events: ['lc', 'rc', 'lr', 'rr'], actions: [null, null, 'chord', null], state: 'idle' },
    { name: 'left-first chord triggers on right release only', events: ['lc', 'rc', 'rr', 'lr'], actions: [null, null, 'chord', null], state: 'idle' },
    { name: 'right-first chord preserves the initial right action', events: ['rc', 'lc', 'lr', 'rr'], actions: ['right', null, 'chord', null], state: 'idle' },
    { name: 'right-first chord also accepts right release first', events: ['rc', 'lc', 'rr', 'lr'], actions: ['right', null, 'chord', null], state: 'idle' },
    { name: 'repeats chords while holding right without repeating right actions', events: ['rc', 'lc', 'lr', 'lc', 'lr', 'rr'], actions: ['right', null, 'chord', null, 'chord', null], state: 'idle' },
    { name: 'repeats chords while holding left without extra left or right actions', events: ['lc', 'rc', 'rr', 'rc', 'rr', 'lr'], actions: [null, null, 'chord', null, 'chord', null], state: 'idle' },
    { name: 'separate left clicks remain left actions', events: ['lc', 'lr', 'lc', 'lr'], actions: [null, 'left', null, 'left'], state: 'idle' },
    { name: 'ignores releases without a preceding press', events: ['lr', 'rr', 'lr', 'rr'], actions: [null, null, null, null], state: 'idle' },
    { name: 'ignores duplicate presses and releases during a chord', events: ['lc', 'lc', 'rc', 'rc', 'lr', 'lr', 'rr', 'rr'], actions: [null, null, null, null, 'chord', null, null, null], state: 'idle' },
    { name: 'does not flag again on a duplicate right press', events: ['rc', 'rc', 'rr', 'rr'], actions: ['right', null, null, null], state: 'idle' },
];

const heldStates: { state: ClassicMouseState; events: ClassicMouseEvent[] }[] = [
    { state: 'idle', events: [] },
    { state: 'left-down', events: ['lc'] },
    { state: 'right-down', events: ['rc'] },
    { state: 'both-down', events: ['lc', 'rc'] },
    { state: 'chord-left-down', events: ['lc', 'rc', 'rr'] },
    { state: 'chord-right-down', events: ['lc', 'rc', 'lr'] },
];

describe('ClassicMouseAutomaton', () => {
    it.each(sequences)('$name', ({ events, actions, state }) => {
        const mouse = new ClassicMouseAutomaton();

        expect(events.map((event) => mouse.step(event))).toEqual(actions);
        expect(mouse.state).toBe(state);
    });

    it.each(heldStates)('moving preserves $state without triggering an action', ({ events, state }) => {
        const mouse = new ClassicMouseAutomaton();
        for (const event of events) mouse.step(event);

        expect(mouse.state).toBe(state);
        expect(mouse.step('mv')).toBeNull();
        expect(mouse.state).toBe(state);
    });

    it.each(heldStates)('cancels $state without turning trailing releases into actions', ({ events }) => {
        const mouse = new ClassicMouseAutomaton();
        for (const event of events) mouse.step(event);

        mouse.reset();

        expect(mouse.state).toBe('idle');
        expect(mouse.step('lr')).toBeNull();
        expect(mouse.step('rr')).toBeNull();
        expect(mouse.step('lc')).toBeNull();
        expect(mouse.step('lr')).toBe('left');
        expect(mouse.state).toBe('idle');
    });

    it('keeps separate games independent', () => {
        const first = new ClassicMouseAutomaton();
        const second = new ClassicMouseAutomaton();

        expect(first.step('lc')).toBeNull();
        expect(second.step('rc')).toBe('right');
        expect(first.step('lr')).toBe('left');
        expect(second.state).toBe('right-down');

        first.reset();

        expect(second.step('lc')).toBeNull();
        expect(second.step('lr')).toBe('chord');
    });
});
