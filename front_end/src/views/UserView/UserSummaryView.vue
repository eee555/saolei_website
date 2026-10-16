<template>
    <div style="display: flex; flex-direction: column; gap: 1rem">
        <ActivityCalendarAbstract :video-list="user.videos" :options="activityCalendarConfig" />
        <BaseCardNormal v-if="user.videos">
            <BBBvSummaryHeader />
            <ElScrollbar aria-orientation="horizontal" :style="{ zoom: BBBvSummaryConfig.zoom }">
                <BBBvSummary level="b" header :video-list="user.videos" />
                <BBBvSummary level="i" :video-list="user.videos" />
                <BBBvSummary level="e" :video-list="user.videos" />
            </ElScrollbar>
        </BaseCardNormal>
        <BaseCardNormal v-if="user.videos" v-experimental>
            <VideoScatter :videos="user.videos" />
        </BaseCardNormal>
    </div>
</template>

<script setup lang="ts">
import { ElScrollbar } from 'element-plus';
import { defineAsyncComponent, ref, watch } from 'vue';

import '@/styles/text.css';
import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import { vExperimental } from '@/components/ExperimentalFeature';
import { fetchUserVideos } from '@/services/userService';
import { activityCalendarConfig, BBBvSummaryConfig } from '@/store';
import { UserProfile } from '@/utils/userprofile';

const ActivityCalendarAbstract = defineAsyncComponent(() => import('@/components/visualization/ActivityCalendarAbstract/App.vue'));
const BBBvSummary = defineAsyncComponent(() => import('@/components/visualization/BBBvSummary/App.vue'));
const BBBvSummaryHeader = defineAsyncComponent(() => import('@/components/visualization/BBBvSummary/Header.vue'));
const VideoScatter = defineAsyncComponent(() => import('@/components/visualization/VideoScatter/App.vue'));

const user = defineModel('user', { type: UserProfile, required: true });

const loading = ref(false);

async function refresh() {
    if (loading.value) return;
    if (user.value.id < 1) return;
    if (user.value.videos === undefined) {
        await refreshVideos();
    }
}

watch(user, refresh, { immediate: true });

async function refreshVideos() {
    if (loading.value) return;
    if (user.value.id < 1) return;
    loading.value = true;
    user.value.videos = await fetchUserVideos(user.value.id);
    loading.value = false;
}
</script>
