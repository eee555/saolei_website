<template>
    <Title :tournament="tournament" />
    <Description />
    <template v-if="([TournamentState.Preparing, TournamentState.Ongoing] as TournamentState[]).includes(tournament.displayState)">
        <h3>{{ t('gsc.howToParticipate') }}</h3>
        <TokenGuide
            v-model:identifier="personaltoken"
            v-model:participant="participant"
            :order="order"
            :token="token"
            @refresh="refresh"
        />
    </template>
    <template v-if="tournament.displayState === TournamentState.Ongoing && store.login_status === LoginStatus.IsLogin && participant">
        <h3>
            {{ t('gsc.realTimeScore') }}&nbsp;
            <ElLink underline="never" :disabled="loading">
                <BaseIconRefresh @click="refresh" />
            </ElLink>
        </h3>
        <PersonalView v-loading="loading" :user-id="store.user.id" :tournament-id="tournament.id">
            <template #personalSummary="{ videos }">
                <GSCPersonalSummary :videos="videos" />
            </template>
        </PersonalView>
    </template>
    <template v-if="tournament.displayState === TournamentState.Awarded">
        <h3>
            {{ t('gsc.finalResults') }}
        </h3>
        <!-- @vue-generic {GSCParticipant} -->
        <AllParticipants :tournament="tournament" :result="result">
            <template #allSummary="{ data, onParticipantSelect }">
                <AllSummary :data="data" @row-click="onParticipantSelect" />
            </template>
            <template #personalSummary="{ videos }">
                <GSCPersonalSummary :videos="videos" />
            </template>
        </AllParticipants>
    </template>
</template>

<script setup lang="ts">
import { ElLink, vLoading } from 'element-plus';
import { computed, ref, watch } from 'vue';
import type { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import '@/styles/text.css';
import AllParticipants from '../common/AllParticipants.vue';
import PersonalView from '../common/PersonalView.vue';
import Title from '../common/Title.vue';

import AllSummary from './AllSummary.vue';
import Description from './Description.vue';
import TokenGuide from './TokenGuide.vue';

import { BaseIconRefresh } from '@/components/common/icon';
import { httpErrorNotification } from '@/components/Notifications';
import GSCPersonalSummary from '@/components/visualization/GSCPersonalSummary/App.vue';
import { fetchGSCResults, fetchParticipantList } from '@/services/tournamentService';
import { store } from '@/store';
import { LoginStatus } from '@/utils/common/structInterface';
import type { GSCParticipant } from '@/utils/gsc';
import { TournamentState } from '@/utils/ms_const';
import type { Tournament } from '@/utils/tournaments';

const props = defineProps({
    tournament: {
        type: Object as PropType<Tournament>,
        required: true,
    },
});

const { t } = useI18n();

const tournament = computed(() => props.tournament);
const order = computed(() => tournament.value.gscData?.order ?? 0);
const token = computed(() => tournament.value.gscData?.token ?? '');
const result = ref<GSCParticipant[]>([]);
const personaltoken = ref<string>('');
const participant = ref(false);
const loading = ref(false);

async function refresh() {
    loading.value = true;
    try {
        if (tournament.value.displayState === TournamentState.Ongoing) {
            result.value = [];
            const participants = await fetchParticipantList(tournament.value.id);
            const currentParticipant = store.login_status === LoginStatus.IsLogin
                ? participants.find((item) => item.user_id === store.user.id)
                : undefined;
            participant.value = currentParticipant !== undefined;
            personaltoken.value = currentParticipant?.arbiter_identifier__identifier ?? '';
        } else {
            participant.value = false;
            personaltoken.value = '';
            result.value = tournament.value.state === TournamentState.Awarded
                ? await fetchGSCResults(tournament.value.id)
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
