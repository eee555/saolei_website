<template>
    <ElDialog v-model="store.video_list_show">
        <VideoList :videos="store.video_list" :columns="['state', 'upload_time', 'software', 'time', 'bvs', 'ioe', 'thrp', 'corr']" sortable />
    </ElDialog>
</template>

<script setup lang="ts">
import { ElDialog } from 'element-plus';

import VideoList from '@/components/VideoList/App.vue';
import { store } from '@/store';
</script>
