<template>
    <Title :tournament="tournament" />
    <Description />
    <template v-if="([TournamentState.Preparing, TournamentState.Ongoing] as TournamentState[]).includes(tournament.displayState)">
        <h3>{{ t('gsc.howToParticipate') }}</h3>
        <TokenGuide
            v-model:token="token"
            :participant="participant"
            :registration-open="tournament.displayState === TournamentState.Ongoing"
            :tournament-id="tournament.id"
            @refresh="refresh"
        />
    </template>
    <template v-if="tournament.displayState === TournamentState.Ongoing && store.login_status === LoginStatus.IsLogin && participant !== null">
        <h3>
            {{ t('gsc.realTimeScore') }}&nbsp;
            <ElLink data-cy="weekly-score-refresh" underline="never" :disabled="loading">
                <BaseIconRefresh @click="refresh" />
            </ElLink>
        </h3>
        <PersonalView :key="personalViewKey" v-loading="loading" :user-id="store.user.id" :tournament-id="tournament.id">
            <template #personalSummary="{ videos }">
                <PersonalSummary :tournament-format="tournament.weeklyData?.tournament_format" :videos="videos" />
            </template>
        </PersonalView>
    </template>
    <template v-if="tournament.displayState === TournamentState.Awarded">
        <h3>
            {{ t('gsc.finalResults') }}
        </h3>
        <!-- @vue-generic {WeeklyParticipant} -->
        <AllParticipants :tournament="tournament" :result="result">
            <template #allSummary="{ data, onParticipantSelect }">
                <AllSummary :data="data" @row-click="onParticipantSelect" />
            </template>
            <template #personalSummary="{ videos }">
                <PersonalSummary :tournament-format="tournament.weeklyData?.tournament_format" :videos="videos" />
            </template>
        </AllParticipants>
    </template>
</template>

<script setup lang="ts">
import { ElLink, vLoading } from 'element-plus';
import { ref, watch } from 'vue';
import type { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import '@/styles/text.css';
import AllParticipants from '../common/AllParticipants.vue';
import PersonalView from '../common/PersonalView.vue';
import Title from '../common/Title.vue';

import AllSummary from './AllSummary.vue';
import Description from './Description.vue';
import PersonalSummary from './PersonalSummary.vue';
import TokenGuide from './TokenGuide.vue';

import { BaseIconRefresh } from '@/components/common/icon';
import { httpErrorNotification } from '@/components/Notifications';
import { fetchParticipantList, fetchWeeklyResults } from '@/services/tournamentService';
import { store } from '@/store';
import { LoginStatus } from '@/utils/common/structInterface';
import { TournamentState } from '@/utils/ms_const';
import type { Tournament, TournamentParticipant } from '@/utils/tournaments';
import type { WeeklyParticipant } from '@/utils/weekly';

const props = defineProps({
    tournament: {
        type: Object as PropType<Tournament>,
        required: true,
    },
});

const { t } = useI18n();

const token = ref<string>('');
const participant = ref<TournamentParticipant | null>(null);
const result = ref<WeeklyParticipant[]>([]);
const loading = ref(false);
const personalViewKey = ref(0);

async function refresh() {
    loading.value = true;
    try {
        if (props.tournament.displayState === TournamentState.Ongoing) {
            result.value = [];
            const participants = await fetchParticipantList(props.tournament.id);
            participant.value = store.login_status === LoginStatus.IsLogin
                ? participants.find((item) => item.user_id === store.user.id) ?? null
                : null;
            token.value = participant.value?.token ?? '';
            personalViewKey.value += 1;
        } else {
            participant.value = null;
            token.value = '';
            result.value = props.tournament.state === TournamentState.Awarded
                ? await fetchWeeklyResults(props.tournament.id)
                : [];
        }
    } catch (error) {
        httpErrorNotification(error);
    }
    loading.value = false;
}

watch(() => [
    props.tournament.id,
    props.tournament.state,
    props.tournament.startDate?.getTime(),
    props.tournament.endDate?.getTime(),
    store.login_status,
], refresh, { immediate: true });
</script>
