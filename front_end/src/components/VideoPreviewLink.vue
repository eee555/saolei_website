<template>
    <a v-if="id != null && id > 0" :href="`#/video/${id}`" class="link video-preview-link" @click="handleClick" @auxclick.stop>
        <slot />
    </a>
    <span v-else>--</span>
</template>

<script setup lang="ts">
import '@/styles/link.css';
import type { PropType } from 'vue';

import { preview } from '@/utils/common/PlayerDialog';
import type { MS_Software } from '@/utils/ms_const';

const props = defineProps({
    id: { type: Number as PropType<number | null>, default: 0 },
    software: { type: String as PropType<MS_Software>, default: undefined },
});

defineSlots<{
    default: () => unknown;
}>();

function handleClick(event: MouseEvent) {
    event.stopPropagation();
    if (event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    void preview(props.id, props.software);
}
</script>

<style scoped>
.video-preview-link {
    color: inherit;
    font: inherit;
    cursor: pointer;
}
</style>
