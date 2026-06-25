<template>
    <ElTabs>
        <ElTabPane :label="t('gsc.summary')" lazy>
            <GSCPersonalSummary :videos="videos" />
        </ElTabPane>
        <ElTabPane :label="t('gsc.videos')" lazy>
            <MultiSelector v-model="VideoListConfig.tournament" :options="thisColumnChoices" :labels="thisColumnChoices.map((s) => t(`common.prop.${s}`))" />
            <VideoList :videos="videos" :columns="VideoListConfig.tournament" sortable paginator />
        </ElTabPane>
        <ElTabPane :label="t('gsc.bbbvSummary')" lazy>
            <BBBvSummaryHeader />
            <BBBvSummary level="b" header :video-list="videos" />
            <BBBvSummary level="i" :video-list="videos" />
            <BBBvSummary level="e" :video-list="videos" />
        </ElTabPane>
        <ElTabPane :label="t('tournament.management')" lazy>
            <ElButton @click="handleDownload">
                {{ t('tournament.downloadParticipant') }}{{ t('common.punct.lparen') }}{{ t('common.ratelimit.oncePerMinute') }}{{ t('common.punct.rparen') }}
            </ElButton>
        </ElTabPane>
    </ElTabs>
</template>

<script setup lang="ts">
import { ElButton, ElTabPane, ElTabs } from 'element-plus';
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import { httpErrorNotification } from '@/components/Notifications';
import VideoList from '@/components/VideoList/App.vue';
import BBBvSummary from '@/components/visualization/BBBvSummary/App.vue';
import BBBvSummaryHeader from '@/components/visualization/BBBvSummary/Header.vue';
import GSCPersonalSummary from '@/components/visualization/GSCPersonalSummary/App.vue';
import MultiSelector from '@/components/widgets/MultiSelector.vue';
import { VideoListConfig } from '@/store';
import { ArrayUtils } from '@/utils/arrays';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { streamToZip } from '@/utils/fileIO';
import { ColumnChoices } from '@/utils/ms_const';
import { VideoAbstract } from '@/utils/videoabstract';

const props = defineProps({
    userId: {
        type: Number,
        required: true,
    },
    tournamentId: {
        type: Number,
        required: true,
    },
});
const { proxy } = useCurrentInstance();
const { t } = useI18n();
const thisColumnChoices = ArrayUtils.sortByReferenceOrder(['bv', 'bvs', 'stnb', 'ces', 'cls', 'corr', 'end_time', 'ioe', 'level', 'state', 'software', 'thrp', 'time', 'upload_time', 'path', 'file_size'], ColumnChoices);

const videos = ref<VideoAbstract[]>([]);

function refresh() {
    if (!props.userId || !props.tournamentId) return;
    proxy.$axios.get('tournament/get_videos/participant/', {
        params: {
            user_id: props.userId,
            tournament_id: props.tournamentId,
        },
    }).then((response) => {
        videos.value = (response.data.data as any[]).map((v) => new VideoAbstract(v));
    }).catch(httpErrorNotification);
}

watch(props, refresh, { immediate: true });

function handleDownload() {
    void proxy.$axios.get('tournament/download/participant/', {
        params: {
            user_id: props.userId,
            tournament_id: props.tournamentId,
        },
        responseType: 'arraybuffer',
    }).then((response) => {
        void streamToZip(new Uint8Array(response.data), `gsc_${props.userId}.zip`);
    }).catch(httpErrorNotification);
}
</script>
