<template>
    <Main v-if="state === 'main'" @enter-auto="state = 'auto'" @enter-help="state = 'help'" @enter-queue="state = 'queue'" />
    <Helper v-if="state === 'help'" @enter-auto="state = 'auto'" @enter-queue="state = 'queue'" @back="state = 'main'" />
    <ImportAll v-if="state === 'auto'" :user-id="store.user.id" @back="state = 'main'" />
    <VideoImportQueue v-if="state === 'queue'" :saolei-id="saoleiId" @back="state = 'main'" />
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref } from 'vue';

import { store } from '@/store';

const Main = defineAsyncComponent(() => import('./Main.vue'));
const Helper = defineAsyncComponent(() => import('./Helper.vue'));
const ImportAll = defineAsyncComponent(() => import('./ImportAll.vue'));
const VideoImportQueue = defineAsyncComponent(() => import('./VideoImportQueue.vue'));

defineProps({
    saoleiId: {
        type: Number,
        required: true,
    },
});

const state = ref('main');
</script>
