<template>
    <UserAvatar :user-id="userId" style="height: 1em" />
    <span>{{ name }}</span>
</template>

<script setup lang="ts">
import UserAvatar from './UserAvatar.vue';

defineProps({
    userId: { type: Number, required: true },
    name: { type: String, default: '' },
});

</script>
