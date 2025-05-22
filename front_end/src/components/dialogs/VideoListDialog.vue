<template>
    <el-dialog v-model="store.video_list_show">
        <video-list :videos="store.video_list" :columns="['state', 'upload_time', 'software', 'time', 'bvs', 'ioe', 'thrp', 'corr']" sortable />
    </el-dialog>
</template>

<script setup lang="ts">

import { ElDialog } from 'element-plus';
import { store } from '@/store';
import VideoList from '@/components/VideoList/App.vue';

</script>
