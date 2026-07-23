<template>
    <ElTabPane v-loading="loadingStatus == QueueRefreshStatus.Refreshing" class="bottom_tabs" lazy name="newest">
        <template #label>
            {{ t('home.latestScore') }}&nbsp;
            <span v-if="loadingStatus == QueueRefreshStatus.CoolingDown" class="text text-success">
                <ElIcon>
                    <Check />
                </ElIcon>
            </span>
            <ElLink
                v-else-if="isActive" underline="never"
                :disabled="loadingStatus != QueueRefreshStatus.Available" style="vertical-align: baseline;" @click="refresh"
            >
                <BaseIconRefresh />
            </ElLink>
        </template>
        <VideoList :videos="queue" :columns="columnChoices" sortable paginator />
    </ElTabPane>
</template>

<script setup lang='ts'>
import { ElIcon, ElLink, ElTabPane, vLoading } from 'element-plus';
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import { QueueRefreshStatus } from './utils';

import { BaseIconRefresh } from '@/components/common/icon';
import VideoList from '@/components/VideoList/App.vue';
import { ArrayUtils } from '@/utils/arrays';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import type { ColumnChoice } from '@/utils/ms_const';
import { VideoAbstract } from '@/utils/videoabstract';

defineProps({
    isActive: { type: Boolean },
});

const { proxy } = useCurrentInstance();
const { t } = useI18n();

const queue = ref<VideoAbstract[]>([]);
const columnChoices = ['state', 'upload_time', 'player', 'software', 'mode', 'level', 'time', 'bv', 'bvs', 'ioe', 'thrp'] as ColumnChoice[];

const loadingStatus = ref(QueueRefreshStatus.Refreshing);

onMounted(refresh);

async function refresh() {
    loadingStatus.value = QueueRefreshStatus.Refreshing;
    setTimeout(() => {
        loadingStatus.value = QueueRefreshStatus.Available;
    }, 5000);
    await proxy.$axios.get('/video/newest_queue/', {
        params: {},
    }).then(function (response) {
        ArrayUtils.empty(queue.value);
        for (const key in response.data) {
            const videoid = Number.parseInt(key);
            const videoinfo = JSON.parse(response.data[key] as string);
            queue.value.push(VideoAbstract.fromVideoRedisInfo(videoid, videoinfo));
        }
    });
    if (loadingStatus.value == QueueRefreshStatus.Refreshing) {
        loadingStatus.value = QueueRefreshStatus.CoolingDown;
    }
}
</script>
