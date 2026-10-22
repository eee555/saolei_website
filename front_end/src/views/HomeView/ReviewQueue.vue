<template>
    <ElTabPane :label="t('home.reviewQueue')" class="bottom_tabs" lazy name="review">
        <VideoList v-loading="loadingStatus" :videos="queue" :columns="video_columns" paginator />
    </ElTabPane>
</template>

<script setup lang='ts'>
import { ElTabPane, vLoading } from 'element-plus';
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import VideoList from '@/components/VideoList/App.vue';
import { fetchVideoList } from '@/services/videoService';
import type { ColumnChoice } from '@/utils/ms_const';
import type { VideoAbstract } from '@/utils/videoabstract';

const { t } = useI18n();

const queue = ref<VideoAbstract[]>([]);
const loadingStatus = ref(true);
const video_columns = ['state', 'upload_time', 'player', 'software', 'mode', 'level', 'time', 'bv', 'bvs', 'ioe', 'thrp'] as ColumnChoice[];

onMounted(refresh);

async function refresh() {
    loadingStatus.value = true;
    try {
        queue.value = await fetchVideoList('/api/video/review_queue');
    } finally {
        loadingStatus.value = false;
    }
}
</script>
