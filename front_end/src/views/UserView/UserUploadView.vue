<template>
    <VideoUpload :is-user-anonymous="user.isAnonymous" :identifiers="user.identifiers" @on-upload="handleUpload" />
</template>

<script setup lang="ts">
import VideoUpload from '@/components/VideoUpload/App.vue';
import { UserProfile } from '@/utils/userprofile';
import type { VideoAbstract } from '@/utils/videoabstract';

const user = defineModel('user', { type: UserProfile, required: true });

function handleUpload(video: VideoAbstract) {
    user.value.videos ??= [];
    user.value.videos.push(video);
}
</script>
