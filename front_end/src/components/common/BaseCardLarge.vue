<template>
    <div class="card card-large">
        <slot />
    </div>
</template>

<script setup lang="ts">
import '@/styles/cards.css';

defineSlots<{
    default?: () => unknown;
}>();
</script>
