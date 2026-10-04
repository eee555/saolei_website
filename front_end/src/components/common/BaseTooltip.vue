<template>
    <Tippy :delay="[showDelay, hideDelay]" :duration="[showAnimation, hideAnimation]" :follow-cursor="followCursor" placement="auto-start">
        <slot />
        <template #content>
            <div class="card card-small">
                <slot name="content" />
            </div>
        </template>
    </Tippy>
</template>

<script setup lang="ts">
import '@/styles/cards.css';
import { Tippy } from 'vue-tippy';

defineProps({
    showDelay: { type: Number, default: 0 },
    hideDelay: { type: Number, default: 0 },
    showAnimation: { type: Number, default: 300 },
    hideAnimation: { type: Number, default: 250 },
    followCursor: { type: Boolean, default: false },
});

defineSlots<{
    default?: () => unknown;
    content?: () => unknown;
}>();
</script>
