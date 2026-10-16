<template>
    <span class="navigation-label" :class="{ 'navigation-label--icon': item.iconOnly }" :data-cy="item.testId">
        <i v-if="item.icon" class="pi" :class="[item.icon]" aria-hidden="true" />
        <span class="navigation-label__text">{{ item.label }}</span>
        <i v-if="item.checked && item.icon" class="navigation-label__check pi pi-check" aria-hidden="true" />
    </span>
</template>

<script setup lang="ts">
import type { PropType } from 'vue';

import type { NavigationItem } from './types';

defineProps({ item: { type: Object as PropType<NavigationItem>, required: true } });
</script>
