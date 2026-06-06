<template>
    <div style="display: flex; flex-direction: column; gap: 1rem">
        <ActivityCalendarAbstract :video-list="user.videos" :options="activityCalendarConfig" :dark-mode="local.darkmode" />
        <base-card-normal v-if="user.videos">
            <BBBvSummaryHeader />
            <el-scrollbar aria-orientation="horizontal" :style="{ zoom: BBBvSummaryConfig.zoom }">
                <BBBvSummary level="b" header :video-list="user.videos" />
                <BBBvSummary level="i" :video-list="user.videos" />
                <BBBvSummary level="e" :video-list="user.videos" />
            </el-scrollbar>
        </base-card-normal>
        <base-card-normal v-if="user.videos" v-experimental>
            <VideoScatter :videos="user.videos" />
        </base-card-normal>
        <div>
            <b class="text text-medium">
                {{ t('identifierManager.title') }}
            </b>
            &nbsp;
            <base-overlay>
                <base-icon-info />
                <template #overlay>
                    <IdentifierHelper style="width: 60%; min-width: 400px; max-width: 100%; margin: auto; display: block" />
                </template>
            </base-overlay>
            <IdentifierManager v-model:user="user" />
        </div>
    </div>
</template>

<script setup lang="ts">
import { ElScrollbar } from 'element-plus';
import { defineAsyncComponent, onMounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import '@/styles/text.css';
import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import BaseOverlay from '@/components/common/BaseOverlay.vue';
import { BaseIconInfo } from '@/components/common/icon';
import { vExperimental } from '@/components/ExperimentalFeature';
import IdentifierManager from '@/components/widgets/IdentifierManager.vue';
import { fetchUserVideos } from '@/services/userService';
import { activityCalendarConfig, BBBvSummaryConfig, local } from '@/store';
import { UserProfile } from '@/utils/userprofile';

const { t } = useI18n();
const IdentifierHelper = defineAsyncComponent(() => import('@/components/dialogs/IdentifierHelper.vue'));
const ActivityCalendarAbstract = defineAsyncComponent(() => import('@/components/visualization/ActivityCalendarAbstract/App.vue'));
const BBBvSummary = defineAsyncComponent(() => import('@/components/visualization/BBBvSummary/App.vue'));
const BBBvSummaryHeader = defineAsyncComponent(() => import('@/components/visualization/BBBvSummary/Header.vue'));
const VideoScatter = defineAsyncComponent(() => import('@/components/visualization/VideoScatter.vue'));

const user = defineModel('user', { type: UserProfile, required: true });

const loading = ref(false);

async function refresh() {
    if (loading.value) return;
    if (user.value.id < 1) return;
    if (user.value.videos === undefined) {
        loading.value = true;
        user.value.videos = await fetchUserVideos(user.value.id);
        loading.value = false;
    }
}

watch(() => user.value.id, refresh, { immediate: true });

onMounted(refresh);

</script>
