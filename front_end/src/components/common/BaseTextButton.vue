<template>
    <BaseButton v-bind="$attrs" :size="size" text class="text" :class="sizeClass">
        <slot />
    </BaseButton>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import type { PropType } from 'vue';
import { computed } from 'vue';

import BaseButton from './BaseButton.vue';

const props = defineProps({
    size: { type: String as PropType<'small' | 'default' | 'large'>, default: 'default' },
});

defineOptions({ inheritAttrs: false });

defineSlots<{
    default?: () => unknown;
}>();

const sizeClass = computed(() => {
    if (props.size === 'small') return 'text-small';
    if (props.size === 'large') return 'text-medium';
    return '';
});
</script>
