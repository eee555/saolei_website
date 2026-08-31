<template>
    <ElTabs>
        <ElTabPane :label="t('local.summary')" lazy>
            <slot name="personalSummary" :videos="videos" />
        </ElTabPane>
        <ElTabPane :label="t('local.videos')" lazy>
            <MultiSelector v-model="VideoListConfig.tournament" :options="thisColumnChoices" :labels="thisColumnChoices.map((s) => t(`common.prop.${s}`))" />
            <VideoList :videos="videos" :columns="VideoListConfig.tournament" sortable paginator />
        </ElTabPane>
        <ElTabPane :label="t('local.management')" lazy>
            <ElButton @click="handleDownload">
                {{ t('local.downloadParticipant') }}{{ t('common.punct.lparen') }}{{ t('common.ratelimit.oncePerMinute') }}{{ t('common.punct.rparen') }}
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
import MultiSelector from '@/components/widgets/MultiSelector.vue';
import { downloadParticipantTournamentVideos, fetchParticipantVideos } from '@/services/tournamentService';
import { VideoListConfig } from '@/store';
import { ArrayUtils } from '@/utils/arrays';
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

const thisColumnChoices = ArrayUtils.sortByReferenceOrder(['upload_time', 'software', 'level', 'time', 'bv', 'bvs', 'stnb', 'ioe', 'thrp', 'path', 'file_size'], ColumnChoices);

const videos = ref<VideoAbstract[]>([]);

function refresh() {
    if (!props.userId || !props.tournamentId) return;
    fetchParticipantVideos({
        userId: props.userId,
        tournamentId: props.tournamentId,
    }).then((data) => {
        videos.value = data.map((video) => new VideoAbstract(video));
    }).catch(httpErrorNotification);
}

watch(props, refresh, { immediate: true });

function handleDownload() {
    void downloadParticipantTournamentVideos({
        userId: props.userId,
        tournamentId: props.tournamentId,
    }).then((data) => {
        void streamToZip(new Uint8Array(data), `weekly_${props.userId}.zip`);
    }).catch(httpErrorNotification);
}

const i18nMessages = {
    'zh-cn': { local: {
        downloadParticipant: '下载录像包',
        management: '管理',
        summary: '概览',
        videos: '录像',
    } },
    en: { local: {
        downloadParticipant: 'Download videos',
        management: 'Management',
        summary: 'Summary',
        videos: 'Videos',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>
