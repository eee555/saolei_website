<template>
    <VideoUpload :is-user-anonymous="user.isAnonymous" @on-upload="handleUpload" />
</template>

<script setup lang="ts">
import VideoUpload from '@/components/VideoUpload/App.vue';
import { invalidateProfileData } from '@/services/profileDataService';
import { UserProfile } from '@/utils/userprofile';

const user = defineModel('user', { type: UserProfile, required: true });

function handleUpload() {
    invalidateProfileData(user.value.id);
}
</script>
