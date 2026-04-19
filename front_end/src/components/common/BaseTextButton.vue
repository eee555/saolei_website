<template>
    <span :class="['text', sizeClass, typeClass]" style="cursor: pointer;" @mouseenter="hovering = true" @mouseleave="hovering = false">
        <slot />
    </span>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import { computed, PropType, ref } from 'vue';

const props = defineProps({
    size: { type: String as PropType<'small' | 'default' | 'large'>, default: 'default' },
});

const hovering = ref(false);

const sizeClass = computed(() => {
    if (props.size === 'small') return 'text-small';
    if (props.size === 'large') return 'text-medium';
    return '';
});

const typeClass = computed(() => {
    return hovering.value ? 'text-primary' : '';
});

</script>
