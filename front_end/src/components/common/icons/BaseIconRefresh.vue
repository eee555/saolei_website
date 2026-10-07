<template>
    <i class="pi pi-refresh" :class="{ 'pi-spin': loading }" />
</template>

<script setup lang="ts">
import 'primeicons/primeicons.css';

defineProps({
    loading: { type: Boolean, default: false },
});
</script>
