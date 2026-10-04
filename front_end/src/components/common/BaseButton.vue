<template>
    <button
        class="base-button" :class="[`base-button--${type}`, `base-button--size-${size}`, { 'base-button--text': text, 'base-button--plain': plain }]"
        :type="nativeType" :disabled="disabled || loading" :aria-busy="loading || undefined" @click="handleClick"
    >
        <i v-if="loading" class="pi pi-spin pi-spinner" aria-hidden="true" />
        <slot v-else name="icon" />
        <slot />
    </button>
</template>

<script setup lang="ts">
import '@/styles/button.css';
import 'primeicons/primeicons.css';
import type { PropType } from 'vue';

const props = defineProps({
    type: { type: String as PropType<'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info'>, default: 'default' },
    size: { type: String as PropType<'small' | 'default' | 'large'>, default: 'default' },
    nativeType: { type: String as PropType<'button' | 'submit' | 'reset'>, default: 'button' },
    text: { type: Boolean, default: false },
    plain: { type: Boolean, default: false },
    disabled: { type: Boolean, default: false },
    loading: { type: Boolean, default: false },
});

const emit = defineEmits<{
    click: [event: MouseEvent];
}>();

defineSlots<{
    default?: () => unknown;
    icon?: () => unknown;
}>();

function handleClick(event: MouseEvent) {
    if (props.disabled || props.loading) {
        event.preventDefault();
        event.stopPropagation();
        return;
    }
    emit('click', event);
}
</script>
