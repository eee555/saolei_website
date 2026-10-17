<template>
    <TopSummary :user-id="user.id" :active="active" :revision="dataKey" />
</template>

<script setup lang="ts">
import { computed, onActivated, onDeactivated, ref } from 'vue';
import { useRoute } from 'vue-router';

import TopSummary from './TopSummary.vue';

import { profileDataRevision } from '@/services/profileDataService';
import { store } from '@/store';
import { UserProfile } from '@/utils/userprofile';

const user = defineModel('user', { type: UserProfile, required: true });
const route = useRoute();
const activated = ref(true);
onActivated(() => {
    activated.value = true;
});
onDeactivated(() => {
    activated.value = false;
});
const active = computed(() => activated.value && route.name === 'user-top' && Number(route.params.id) === user.value.id);
const dataKey = computed(() => `${user.value.id}:${store.sessionRevision}:${profileDataRevision(user.value.id)}`);
</script>
