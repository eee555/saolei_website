<template>
    <h1>
        {{ t('gsc.title', { order: order }) }}
        <TournamentStateIcon :state="tournament.state" />
    </h1>
    {{ t('gsc.schedule') }}{{ t('common.punct.colon') }}
    <el-text>
        {{ tournament.displayStartTime() }}
        &nbsp;~&nbsp;
        {{ tournament.displayEndTime() }}
    </el-text>
    &nbsp;
    <br>
    {{ t('gsc.description.line1') }}
    <br>
    {{ t('gsc.description.line2') }}
    <br>
    <template v-if="[TournamentState.Preparing, TournamentState.Ongoing].includes(tournament.state)">
        <h3>{{ t('gsc.howToParticipate') }}</h3>
        <GSCTokenGuide v-model="personaltoken" :order="order" :token="token" />
    </template>
    <template v-if="tournament.state === TournamentState.Ongoing">
        <h3>
            {{ t('gsc.realTimeScore') }}&nbsp;
            <base-icon-refresh @click="refresh" />
        </h3>
        <el-tabs>
            <el-tab-pane :label="t('gsc.summary')" lazy>
                <GSCPersonalSummary :videos="personalVideos" />
            </el-tab-pane>
            <el-tab-pane :label="t('gsc.videos')" lazy>
                <MultiSelector v-model="VideoListConfig.tournament" :options="thisColumnChoices" :labels="thisColumnChoices.map((s) => t(`common.prop.${s}`))" />
                <VideoList :videos="personalVideos" :columns="VideoListConfig.tournament" sortable />
            </el-tab-pane>
            <el-tab-pane :label="t('gsc.bbbvSummary')" lazy>
                <BBBvSummaryHeader />
                <BBBvSummary level="b" header :video-list="personalVideos" />
                <BBBvSummary level="i" :video-list="personalVideos" />
                <BBBvSummary level="e" :video-list="personalVideos" />
            </el-tab-pane>
        </el-tabs>
    </template>
    <template v-if="[TournamentState.Finished, TournamentState.Awarded].includes(tournament.state)">
        <h3>
            {{ t('gsc.finalResults') }}
        </h3>
        <GSCAllSummary :data="result" />
    </template>
</template>

<script setup lang="ts">

import { httpErrorNotification } from '@/components/Notifications';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { Tournament } from '@/utils/tournaments';
import { ElText, ElTabs, ElTabPane } from 'element-plus';
import { ref, watch } from 'vue';
import { store, VideoListConfig } from '@/store';
import { LoginStatus } from '@/utils/common/structInterface';
import { TournamentState } from '@/utils/ms_const';
import { GSCParticipant, GSCParticipantDefault } from '@/utils/gsc';
import GSCPersonalSummary from '@/components/visualization/GSCPersonalSummary/App.vue';
import GSCTokenGuide from './GSCTokenGuide.vue';
import BaseIconRefresh from '@/components/common/BaseIconRefresh.vue';
import GSCAllSummary from './GSCAllSummary.vue';
import { useI18n } from 'vue-i18n';
import TournamentStateIcon from '@/components/widgets/TournamentStateIcon.vue';
import { VideoAbstract } from '@/utils/videoabstract';
import VideoList from '@/components/VideoList/App.vue';
import MultiSelector from '@/components/widgets/MultiSelector.vue';
import BBBvSummary from '@/components/visualization/BBBvSummary/App.vue';
import BBBvSummaryHeader from '@/components/visualization/BBBvSummary/Header.vue';

const props = defineProps({
    id: {
        type: Number,
        required: true,
    },
});

const { proxy } = useCurrentInstance();
const { t } = useI18n();
const thisColumnChoices = ['bv', 'bvs', 'stnb', 'ces', 'cls', 'corr', 'end_time', 'ioe', 'level', 'state', 'software', 'thrp', 'time', 'upload_time', 'path', 'file_size'] as const;

const tournament = ref<Tournament>(new Tournament({}));
const order = ref<number>(0);
const token = ref<string>('');
const result = ref<GSCParticipant[]>([]);
const personaltoken = ref<string>('');
const personalresult = ref<GSCParticipant>(GSCParticipantDefault);
const personalVideos = ref<VideoAbstract[]>([]);

function refresh() {
    proxy.$axios.get('tournament/gscinfo/', {
        params: {
            id: props.id,
        },
    }).then((response) => {
        tournament.value = new Tournament(response.data.data);
        order.value = response.data.data.order;
        token.value = response.data.data.token;

        if (tournament.value.state === TournamentState.Ongoing && store.login_status === LoginStatus.IsLogin) {
            result.value = [];
            personaltoken.value = response.data.identifier ? response.data.identifier : '';
            personalVideos.value = response.data.results.map((video: any) => new VideoAbstract(video));
        } else {
            personaltoken.value = '';
            personalresult.value = GSCParticipantDefault;
            result.value = response.data.results;
        }
    }).catch(httpErrorNotification);
}

watch(() => props.id, refresh, { immediate: true });

</script>
