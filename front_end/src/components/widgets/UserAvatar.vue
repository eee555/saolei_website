<template>
    <img
        :src="avatarSrc" loading="lazy"
        style="max-height: 100%; max-width: 100%; aspect-ratio: 1 / 1;"
        @error="avatarSrc = DefaultAvatar"
    >
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

import { DefaultAvatar } from '@/utils/assets';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

const props = defineProps({
    userId: { type: Number, required: true },
});

const { proxy } = useCurrentInstance();

const avatarSrc = ref(DefaultAvatar);

watch(() => props.userId, (newId) => {
    if (newId) {
        avatarSrc.value = `${proxy.$axios.defaults.baseURL}/api/userprofile/avatar/${newId}`;
    } else {
        avatarSrc.value = DefaultAvatar;
    }
}, { immediate: true });
</script>
