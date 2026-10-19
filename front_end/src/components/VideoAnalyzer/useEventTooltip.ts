import { nextTick, shallowRef } from 'vue';
import type { Ref, ShallowRef } from 'vue';
import { useTippy } from 'vue-tippy';

import type { EventPulse, EventSpan } from './customEvents';

export type HoveredCustomEvent = { key: string; type: 'pulse'; pulse: EventPulse } | { key: string; type: 'sustained'; span: EventSpan };

export interface EventTooltipController {
    hovered: ShallowRef<HoveredCustomEvent | null>;
    showTooltip: (event: HoveredCustomEvent, pointer: PointerEvent) => Promise<void>;
    moveTooltip: (pointer: PointerEvent) => void;
    hideTooltip: () => void;
}

export function useEventTooltip(reference: Readonly<Ref<Element | null>>, content: Readonly<Ref<HTMLElement | null>>): EventTooltipController {
    const hovered = shallowRef<HoveredCustomEvent | null>(null);
    let clientX = 0;
    let clientY = 0;
    // Reuse one instance and prepared data across every event in this surface.
    const { tippy, show, hide } = useTippy(reference, {
        content: () => content.value ?? '',
        trigger: 'manual',
        appendTo: () => document.body,
        placement: 'top',
        duration: 0,
        getReferenceClientRect: () => new DOMRect(clientX, clientY, 0, 0),
    });
    function moveTooltip(pointer: PointerEvent) {
        ({ clientX, clientY } = pointer);
        if (hovered.value !== null) void tippy.value?.popperInstance?.update();
    }
    async function showTooltip(event: HoveredCustomEvent, pointer: PointerEvent) {
        hovered.value = event;
        moveTooltip(pointer);
        await nextTick();
        if (hovered.value === event) {
            show();
            void tippy.value?.popperInstance?.update();
        }
    }
    function hideTooltip() {
        hovered.value = null;
        hide();
    }
    return { hovered, showTooltip, moveTooltip, hideTooltip };
}
