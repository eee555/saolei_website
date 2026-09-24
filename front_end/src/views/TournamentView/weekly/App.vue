<template>
    <PublicTournament :tournament="tournament" :participants="participants" :index="index" :loading="loading" :refresh-participants="refresh" :auto-uploader-enabled="!store.isUserAnonymous" :auto-uploader-filter="matchesFilter">
        <template #description>
            <Description />
        </template>
        <template #participationGuide>
            <TokenGuide :token="participant?.token ?? ''" :participant="participant" :registration-open="state === TournamentState.Ongoing" :tournament-id="tournament.id" @registered="registered" />
        </template>
        <template #autoUploaderFilter>
            <AutoUploaderFilter ref="filterControl" :format="format" :participant="participant" />
        </template>
        <template #allSummary="{ data, onParticipantSelect }">
            <AllSummary v-if="state === TournamentState.Awarded" :data="data" @row-click="onParticipantSelect" />
            <RegisteredParticipants v-else :participants="data" :loading="loading" :can-manage="canManage" @deleted="deleted" />
        </template>
        <template #personalSummary="{ videos }">
            <PersonalSummary :tournament-format="format" :videos="videos" />
        </template>
    </PublicTournament>
</template>

<script setup lang="ts">
import { computed, useTemplateRef } from 'vue';

import PublicTournament from '../common/PublicTournament.vue';
import RegisteredParticipants from '../common/RegisteredParticipants.vue';
import { useParticipants } from '../common/useParticipants';

import AllSummary from './AllSummary.vue';
import AutoUploaderFilter from './AutoUploaderFilter.vue';
import Description from './Description.vue';
import PersonalSummary from './PersonalSummary.vue';
import TokenGuide from './TokenGuide.vue';

import { fetchWeeklyResults } from '@/services/tournamentService';
import { store } from '@/store';
import { LoginStatus } from '@/utils/common/structInterface';
import type { AnyVideo } from '@/utils/fileIO';
import { TournamentState } from '@/utils/ms_const';
import { Tournament } from '@/utils/tournaments';
import type { VideoAbstract } from '@/utils/videoabstract';
import { WeeklyParticipant, WeeklyTournamentFormat } from '@/utils/weekly';

const props = defineProps({ tournament: { type: Tournament, required: true } });
const { participants, index, participant, loading, state, refresh, registered, deleted } = useParticipants(() => props.tournament, (item) => new WeeklyParticipant(item), fetchWeeklyResults);
const format = computed(() => props.tournament.weeklyData?.tournament_format ?? WeeklyTournamentFormat.Classic);
const canManage = computed(() => store.login_status === LoginStatus.IsLogin && (store.user.is_staff || store.user.id === props.tournament.hostId));
const filterControl = useTemplateRef<{ matchesFilter: (video: AnyVideo, stat: VideoAbstract) => boolean }>('filterControl');
function matchesFilter(video: AnyVideo, stat: VideoAbstract) {
    return filterControl.value?.matchesFilter(video, stat) ?? false;
}
</script>
