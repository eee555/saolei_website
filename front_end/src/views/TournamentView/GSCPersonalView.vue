<template>
    <el-tabs>
        <el-tab-pane :label="t('gsc.summary')" lazy>
            <GSCPersonalSummary :videos="videos" />
        </el-tab-pane>
        <el-tab-pane :label="t('gsc.videos')" lazy>
            <MultiSelector v-model="VideoListConfig.tournament" :options="thisColumnChoices" :labels="thisColumnChoices.map((s) => t(`common.prop.${s}`))" />
            <VideoList :videos="videos" :columns="VideoListConfig.tournament" sortable />
        </el-tab-pane>
        <el-tab-pane :label="t('gsc.bbbvSummary')" lazy>
            <BBBvSummaryHeader />
            <BBBvSummary level="b" header :video-list="videos" />
            <BBBvSummary level="i" :video-list="videos" />
            <BBBvSummary level="e" :video-list="videos" />
        </el-tab-pane>
        <el-tab-pane :label="t('tournament.management')" lazy>
            <el-button @click="handleDownload">
                {{ t('tournament.downloadParticipant') }}{{ t('common.punct.lparen') }}{{ t('common.ratelimit.oncePerMinute') }}{{ t('common.punct.rparen') }}
            </el-button>
        </el-tab-pane>
    </el-tabs>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { ElTabs, ElTabPane, ElButton } from 'element-plus';
import VideoList from '@/components/VideoList/App.vue';
import MultiSelector from '@/components/widgets/MultiSelector.vue';
import BBBvSummary from '@/components/visualization/BBBvSummary/App.vue';
import BBBvSummaryHeader from '@/components/visualization/BBBvSummary/Header.vue';
import { ref, watch } from 'vue';
import { VideoAbstract } from '@/utils/videoabstract';
import { VideoListConfig } from '@/store';
import GSCPersonalSummary from '@/components/visualization/GSCPersonalSummary/App.vue';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { httpErrorNotification } from '@/components/Notifications';
import { streamToZip } from '@/utils/fileIO';


const { proxy } = useCurrentInstance();
const { t } = useI18n();
const thisColumnChoices = ['bv', 'bvs', 'stnb', 'ces', 'cls', 'corr', 'end_time', 'ioe', 'level', 'state', 'software', 'thrp', 'time', 'upload_time', 'path', 'file_size'] as const;

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

const videos = ref<VideoAbstract[]>([]);

function refresh() {
    if (!props.userId || !props.tournamentId) return;
    proxy.$axios.get('tournament/get_videos/participant/', {
        params: {
            user_id: props.userId,
            tournament_id: props.tournamentId,
        },
    }).then((response) => {
        videos.value = response.data.data.map((v: any) => new VideoAbstract(v));
    }).catch(httpErrorNotification);
}

watch(props, refresh, { immediate: true });

function handleDownload() {
    proxy.$axios.get('tournament/download/participant/', {
        params: {
            user_id: props.userId,
            tournament_id: props.tournamentId,
        },
        responseType: 'arraybuffer',
    }).then((response) => {
        streamToZip(new Uint8Array(response.data), `gsc_${props.userId}.zip`);
    }).catch(httpErrorNotification);
}

</script>
