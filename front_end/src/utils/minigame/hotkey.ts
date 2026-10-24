export type RestartHotkey = Pick<KeyboardEvent, 'code' | 'key' | 'ctrlKey' | 'altKey' | 'shiftKey' | 'metaKey'>;
type HotkeyEvent = RestartHotkey & Pick<KeyboardEvent, 'repeat' | 'isComposing'>;

export function restartHotkeyFromEvent(event: HotkeyEvent): RestartHotkey | null {
    if (event.repeat || event.isComposing || event.code === '' || event.key === '' || ['Control', 'Alt', 'Shift', 'Meta', 'AltGraph', 'Dead', 'Unidentified', 'Process'].includes(event.key)) return null;
    const { code, key, ctrlKey, altKey, shiftKey, metaKey } = event;
    return { code, key, ctrlKey, altKey, shiftKey, metaKey };
}

export function matchesRestartHotkey(hotkey: RestartHotkey | null, event: HotkeyEvent): boolean {
    return hotkey !== null && !event.repeat && !event.isComposing && event.code === hotkey.code && event.ctrlKey === hotkey.ctrlKey && event.altKey === hotkey.altKey && event.shiftKey === hotkey.shiftKey && event.metaKey === hotkey.metaKey;
}

export function formatRestartHotkey(hotkey: RestartHotkey | null): string {
    if (hotkey === null) return '';
    const key = hotkey.key === ' ' ? 'Space' : hotkey.key.length === 1 ? hotkey.key.toUpperCase() : hotkey.key;
    return [hotkey.ctrlKey ? 'Ctrl' : '', hotkey.altKey ? 'Alt' : '', hotkey.shiftKey ? 'Shift' : '', hotkey.metaKey ? 'Meta' : '', key].filter(Boolean).join(' + ');
}
