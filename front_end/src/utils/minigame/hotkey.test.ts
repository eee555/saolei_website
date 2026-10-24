import { describe, expect, it } from 'vitest';

import { formatRestartHotkey, matchesRestartHotkey, restartHotkeyFromEvent } from './hotkey';
import type { RestartHotkey } from './hotkey';

function keyEvent(overrides: Partial<RestartHotkey & Pick<KeyboardEvent, 'repeat' | 'isComposing'>> = {}) {
    return { code: 'KeyR', key: 'r', ctrlKey: false, altKey: false, shiftKey: false, metaKey: false, repeat: false, isComposing: false, ...overrides };
}

describe('minigame restart hotkey', () => {
    it('starts unset and records single keys and exact modifier combinations', () => {
        expect(formatRestartHotkey(null)).toBe('');
        expect(matchesRestartHotkey(null, keyEvent())).toBe(false);
        const hotkey = restartHotkeyFromEvent(keyEvent());
        expect(formatRestartHotkey(hotkey)).toBe('R');
        expect(matchesRestartHotkey(hotkey, keyEvent({ key: 'R' }))).toBe(true);
        for (const modifier of ['ctrlKey', 'altKey', 'shiftKey', 'metaKey'] as const) {
            expect(matchesRestartHotkey(hotkey, keyEvent({ [modifier]: true }))).toBe(false);
            const combination = restartHotkeyFromEvent(keyEvent({ [modifier]: true }));
            expect(matchesRestartHotkey(combination, keyEvent({ [modifier]: true }))).toBe(true);
            expect(matchesRestartHotkey(combination, keyEvent())).toBe(false);
        }
        expect(matchesRestartHotkey(hotkey, keyEvent({ code: 'KeyT' }))).toBe(false);
        expect(formatRestartHotkey(restartHotkeyFromEvent(keyEvent({ ctrlKey: true, shiftKey: true })))).toBe('Ctrl + Shift + R');
        expect(formatRestartHotkey(restartHotkeyFromEvent(keyEvent({ key: ' ', code: 'Space' })))).toBe('Space');
        expect(formatRestartHotkey(restartHotkeyFromEvent(keyEvent({ key: 'F2', code: 'F2' })))).toBe('F2');
    });

    it.each(['Control', 'Alt', 'Shift', 'Meta', 'AltGraph', 'Dead', 'Unidentified', 'Process', ''])('does not record a standalone modifier or input-method key (%s)', (key) => {
        expect(restartHotkeyFromEvent(keyEvent({ key }))).toBeNull();
    });

    it.each([{ repeat: true }, { isComposing: true }, { code: '' }])('ignores repeated, composing or unidentified keystrokes (%j)', (override) => {
        expect(restartHotkeyFromEvent(keyEvent(override))).toBeNull();
        expect(matchesRestartHotkey(restartHotkeyFromEvent(keyEvent()), keyEvent(override))).toBe(false);
    });
});
