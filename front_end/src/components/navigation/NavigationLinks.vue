<template>
    <nav class="navigation-links" :aria-label="label">
        <NavigationControl
            v-for="item in items" :key="item.id" :item="item" :active="active"
            :class="{ 'is-active': active === item.id }" :title="item.label"
            :data-navigation-id="item.id" @navigate="emit('navigate')"
        />
    </nav>
</template>

<script setup lang="ts">
import type { PropType } from 'vue';

import NavigationControl from './NavigationControl.vue';
import type { NavigationItem } from './types';

defineProps({
    items: { type: Array as PropType<NavigationItem[]>, required: true },
    active: { type: String, required: true },
    label: { type: String, required: true },
});
const emit = defineEmits<{ navigate: [] }>();
</script>
