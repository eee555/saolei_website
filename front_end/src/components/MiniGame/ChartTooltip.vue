<template>
    <Tippy ref="tooltip" tag="div" trigger="manual" :duration="0" :get-reference-client-rect="referenceRect">
        <slot />
        <template #content>
            <div class="card card-small text text-small">
                <slot name="content" />
            </div>
        </template>
    </Tippy>
</template>

<script setup lang="ts">
import '@/styles/cards.css';

import { nextTick, useTemplateRef, watch } from 'vue';
import type { PropType } from 'vue';
import { Tippy } from 'vue-tippy';
import type { TippyComponent } from 'vue-tippy';

const props = defineProps({ pointer: { type: Object as PropType<PointerEvent | null>, default: null } });
defineSlots<{ default?: () => unknown; content?: () => unknown }>();
const tooltip = useTemplateRef<TippyComponent>('tooltip');
function referenceRect() {
    return new DOMRect(props.pointer?.clientX ?? 0, props.pointer?.clientY ?? 0, 0, 0);
}
watch(() => props.pointer, async (pointer) => {
    if (pointer === null) tooltip.value?.hide();
    else {
        await nextTick();
        if (props.pointer !== pointer) return;
        tooltip.value?.show();
        void tooltip.value?.tippy?.popperInstance?.update();
    }
});
</script>
