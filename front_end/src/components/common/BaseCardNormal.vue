<template>
    <div class="card">
        <slot />
    </div>
</template>

<script setup lang="ts">
import '@/styles/cards.css';

defineSlots<{
    default?: () => unknown;
}>();
</script>
