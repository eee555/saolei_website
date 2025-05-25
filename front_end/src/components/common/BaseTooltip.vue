<template>
    <tippy :delay="[showDelay, hideDelay]" :duration="[showAnimation, hideAnimation]" :follow-cursor="followCursor" placement="auto-start">
        <slot />
        <template #content>
            <base-card-small>
                <slot name="content" />
            </base-card-small>
        </template>
    </tippy>
</template>

<script setup lang="ts">

import BaseCardSmall from './BaseCardSmall.vue';
import { Tippy } from 'vue-tippy';

defineProps({
    showDelay: { type: Number, default: 0 },
    hideDelay: { type: Number, default: 0 },
    showAnimation: { type: Number, default: 300 },
    hideAnimation: { type: Number, default: 250 },
    followCursor: { type: Boolean, default: false },
});

</script>
