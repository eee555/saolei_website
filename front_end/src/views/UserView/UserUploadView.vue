<template>
    <VideoUpload :is-user-anonymous="user.isAnonymous" :identifiers="user.identifiers" @on-upload="(video) => { user.videos?.push(video); }" />
</template>

<script setup lang="ts">
import VideoUpload from '@/components/VideoUpload/App.vue';
import { UserProfile } from '@/utils/userprofile';

const user = defineModel('user', { type: UserProfile, required: true });
</script>
