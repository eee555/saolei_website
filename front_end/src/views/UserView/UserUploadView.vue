<template>
    <VideoUpload :is-user-anonymous="store.isUserAnonymous" :identifiers="store.user.identifiers" @on-upload="(video) => { store.user.videos.push(video); store.player.videos.push(video); }" />
</template>

<script setup lang="ts">

import VideoUpload from '@/components/VideoUpload/App.vue';
import { store } from '@/store';

</script>
