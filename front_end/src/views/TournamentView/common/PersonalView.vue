<template>
    <ElTabs>
        <ElTabPane :label="t('local.summary')" lazy>
            <slot name="autoUploader" :participant="participant" />
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

<script setup lang="ts" generic="TParticipant extends TournamentParticipant">
import { ElButton, ElTabPane, ElTabs } from 'element-plus';
import { computed, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import { httpErrorNotification } from '@/components/Notifications';
import VideoList from '@/components/VideoList/App.vue';
import MultiSelector from '@/components/widgets/MultiSelector.vue';
import { downloadParticipantTournamentVideos, fetchParticipantVideos } from '@/services/tournamentService';
import { VideoListConfig } from '@/store';
import { ArrayUtils } from '@/utils/arrays';
import { streamToZip } from '@/utils/fileIO';
import { ColumnChoices } from '@/utils/ms_const';
import type { TournamentParticipant } from '@/utils/tournaments';
import { VideoAbstract } from '@/utils/videoabstract';

const participant = defineModel<TParticipant>({ required: true });

defineSlots<{
    autoUploader?: (props: { participant: TParticipant }) => unknown;
    personalSummary?: (props: { videos: VideoAbstract[] }) => unknown;
}>();

const thisColumnChoices = ArrayUtils.sortByReferenceOrder(['upload_time', 'software', 'level', 'mode', 'time', 'bv', 'bvs', 'stnb', 'ioe', 'thrp', 'path', 'file_size'], ColumnChoices);
const videos = computed(() => participant.value.videos ?? []);

function refresh() {
    if (!participant.value.user_id || !participant.value.tournament_id) return;
    participant.value.videos = [];
    fetchParticipantVideos({
        userId: participant.value.user_id,
        tournamentId: participant.value.tournament_id,
    }).then((data) => {
        participant.value.videos = data.map((video) => new VideoAbstract(video));
    }).catch(httpErrorNotification);
}

watch(() => [participant.value.user_id, participant.value.tournament_id], refresh, { immediate: true });

function handleDownload() {
    void downloadParticipantTournamentVideos({
        userId: participant.value.user_id,
        tournamentId: participant.value.tournament_id,
    }).then((data) => {
        void streamToZip(new Uint8Array(data), `weekly_${participant.value.user_id}.zip`);
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
