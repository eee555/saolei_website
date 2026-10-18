<template>
    <RouterLink v-if="item.to" :to="item.to" :aria-label="item.label" :aria-current="active === item.id ? 'page' : undefined" class="navigation-control" @click.stop="onNavigate">
        <NavigationLabel :item="item" />
    </RouterLink>
    <a v-else-if="item.href" :href="item.href" :target="item.target" :rel="item.target === '_blank' ? 'noopener noreferrer' : undefined" :aria-label="item.label" class="navigation-control" @click.stop="onNavigate">
        <NavigationLabel :item="item" />
    </a>
    <button v-else type="button" class="navigation-control" :aria-label="item.label" :aria-pressed="item.checked" @keydown.stop @click.stop="emit('activate', item.id)">
        <NavigationLabel :item="item" />
    </button>
</template>

<script setup lang="ts">
import type { PropType } from 'vue';
import { RouterLink } from 'vue-router';

import NavigationLabel from './NavigationLabel.vue';
import type { NavigationItem } from './types';

defineProps({
    item: { type: Object as PropType<NavigationItem>, required: true },
    active: { type: String, required: true },
});
const emit = defineEmits<{ activate: [id: string]; navigate: [] }>();

function onNavigate(event: MouseEvent) {
    if (event.button === 0 && !event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey) emit('navigate');
}
</script>
