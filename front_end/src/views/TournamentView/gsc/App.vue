<template>
    <PublicTournament :tournament="tournament" :participants="participants" :index="index" :loading="loading" :refresh-participants="refresh" :auto-uploader-enabled="!store.isUserAnonymous" :auto-uploader-filter="matchesFilter">
        <template #description>
            <Description />
        </template>
        <template #participationGuide>
            <TokenGuide :identifier="participant?.arbiter_identifier__identifier ?? ''" :participant="participant" :order="tournament.gscData?.order" :token="token" @refresh="refresh" />
        </template>
        <template #autoUploaderFilter>
            <AutoUploaderFilter ref="filterControl" :participant="participant" />
        </template>
        <template #allSummary="{ data, onParticipantSelect }">
            <AllSummary v-if="state === TournamentState.Awarded" :data="data" @row-click="onParticipantSelect" />
            <RegisteredParticipants v-else :participants="data" :loading="loading" :can-manage="canManage" test-id="gsc-participants" @deleted="deleted" />
        </template>
        <template #personalSummary="{ videos }">
            <GSCPersonalSummary :videos="videos" />
        </template>
    </PublicTournament>
</template>

<script setup lang="ts">
import { computed, ref, useTemplateRef, watch } from 'vue';

import PublicTournament from '../common/PublicTournament.vue';
import RegisteredParticipants from '../common/RegisteredParticipants.vue';
import { useParticipants } from '../common/useParticipants';

import AllSummary from './AllSummary.vue';
import AutoUploaderFilter from './AutoUploaderFilter.vue';
import Description from './Description.vue';
import TokenGuide from './TokenGuide.vue';

import { httpErrorNotification } from '@/components/Notifications';
import GSCPersonalSummary from '@/components/visualization/GSCPersonalSummary/App.vue';
import { fetchGSCResults, fetchTournament } from '@/services/tournamentService';
import { store } from '@/store';
import { LoginStatus } from '@/utils/common/structInterface';
import type { AnyVideo } from '@/utils/fileIO';
import { GSCParticipant } from '@/utils/gsc';
import { TournamentState } from '@/utils/ms_const';
import { Tournament } from '@/utils/tournaments';
import type { VideoAbstract } from '@/utils/videoabstract';

const props = defineProps({ tournament: { type: Tournament, required: true } });
const { participants, index, participant, loading, state, refresh, deleted } = useParticipants(() => props.tournament, (item) => new GSCParticipant(item), fetchGSCResults);
const canManage = computed(() => store.login_status === LoginStatus.IsLogin && (store.user.is_staff || store.user.id === props.tournament.hostId));
const filterControl = useTemplateRef<{ matchesFilter: (video: AnyVideo, stat: VideoAbstract) => boolean }>('filterControl');
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
function matchesFilter(video: AnyVideo, stat: VideoAbstract) {
    return filterControl.value?.matchesFilter(video, stat) ?? false;
}
</script>
