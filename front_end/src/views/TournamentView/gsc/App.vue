<template>
    <PublicTournament :tournament="tournament" :participants="participants" :index="index" :loading="loading" :refresh-participants="refresh" :auto-uploader-enabled="!store.isUserAnonymous" :auto-uploader-filter="matchesFilter">
        <template #description>
            <Description />
        </template>
        <template #participationGuide>
            <TokenGuide :identifier="participant?.arbiter_identifier__identifier ?? ''" :participant="participant" :order="tournament.gscData?.order" :token="token" :identifier-registration-open="state === TournamentState.Ongoing" @refresh="refresh" />
        </template>
        <template #autoUploaderFilter>
            <ElSelect v-model="filterLevel" size="small" style="width: 250px">
                <ElOption :label="t('local.tournament')" value="tournament" />
                <ElOption :label="t('local.supported')" value="supported" />
                <ElOption :label="t('local.bv')" value="bv" />
            </ElSelect>
        </template>
        <template #allSummary="{ data, onParticipantSelect }">
            <AllSummary v-if="state === TournamentState.Awarded" :data="data" @row-click="onParticipantSelect" />
            <Registered v-else :loading="loading" :participants="participants" />
        </template>
        <template #personalSummary="{ videos }">
            <GSCPersonalSummary :videos="videos" />
        </template>
    </PublicTournament>
</template>

<script setup lang="ts">
import { ElOption, ElSelect } from 'element-plus';
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import PublicTournament from '../common/PublicTournament.vue';
import { useParticipants } from '../common/useParticipants';
import type { AutoUploadVideo } from '../common/utils';

import AllSummary from './AllSummary.vue';
import Description from './Description.vue';
import Registered from './Registered.vue';
import TokenGuide from './TokenGuide.vue';

import { httpErrorNotification } from '@/components/Notifications';
import GSCPersonalSummary from '@/components/visualization/GSCPersonalSummary/App.vue';
import { fetchGSCResults, fetchTournament } from '@/services/tournamentService';
import { store } from '@/store';
import { GSCParticipant, isGSCSupportedVideo, meetsGSCBV } from '@/utils/gsc';
import { TournamentState } from '@/utils/ms_const';
import { Tournament } from '@/utils/tournaments';

const props = defineProps({ tournament: { type: Tournament, required: true } });
const { participants, index, participant, loading, state, refresh } = useParticipants(() => props.tournament, (item) => new GSCParticipant(item), fetchGSCResults);
const token = ref(props.tournament.gscData?.token ?? '');
watch(() => props.tournament, (value) => {
    token.value = value.gscData?.token ?? '';
});
watch(state, async (value, previous) => {
    if (value !== TournamentState.Ongoing || previous !== TournamentState.Preparing) return;
    const { id } = props.tournament;
    try {
        const updated = new Tournament(await fetchTournament(id));
        if (id === props.tournament.id) token.value = updated.gscData?.token ?? '';
    } catch (error) {
        httpErrorNotification(error);
    }
});

const filterLevel = ref('bv');

function matchesFilter(video: AutoUploadVideo): boolean {
    if (!participant.value) return false;
    if (video.stat.software === 'a') {
        if (!video.identifier || video.identifier !== participant.value.arbiter_identifier__identifier) return false;
    } else {
        if (!participant.value.token || !video.tokens.includes(participant.value.token)) return false;
    }
    if (filterLevel.value === 'tournament') return true;
    if (!isGSCSupportedVideo(video.stat)) return false;
    if (filterLevel.value === 'supported') return true;
    return meetsGSCBV(video.stat);
}

const i18nMessages = {
    'zh-cn': { local: {
        tournament: '所有比赛录像',
        supported: '级别和模式符合',
        bv: '3BV 下限符合',
    } },
    en: { local: {
        tournament: 'All tournament videos',
        supported: 'Supported levels and modes',
        bv: '3BV minimum met',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>
