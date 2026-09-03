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
    <template v-if="([TournamentState.Finished, TournamentState.Awarded] as TournamentState[]).includes(tournament.displayState)">
        <h3>
            {{ t('gsc.finalResults') }}
        </h3>
        <ElTabs v-model="allSummaryTabPosition">
            <ElTabPane :label="t('tournament.ranking')" lazy :name="-1">
                <ElButton v-if="tournament.state === TournamentState.Awarded" size="small" @click="downloadAll">
                    {{ t('tournament.downloadAll') }}{{ t('common.punct.lparen') }}{{ t('common.ratelimit.oncePerHour') }}{{ t('common.punct.rparen') }}
                </ElButton>
                <ElRow style="height: 0.5em" />
                <AllSummary :data="result" @row-click="handleAllSummaryRowClick" />
            </ElTabPane>
            <ElTabPane v-for="(participant, index) in viewedParticipants" :key="participant.id" lazy :name="index">
                <template #label>
                    <PlayerName v-if="participant.user_id !== null" :user-id="participant.user_id" />
                    &nbsp;
                    <ElLink underline="never" @click="handleAllSummaryTabClose(index)">
                        <BaseIconClose style="scale: 65%" />
                    </ElLink>
                </template>
                <PersonalView v-if="participant.user_id !== null" :user-id="participant.user_id" :tournament-id="tournament.id">
                    <template #personalSummary="{ videos }">
                        <PersonalSummary :tournament-format="tournament.weeklyData?.tournament_format" :videos="videos" />
                    </template>
                </PersonalView>
            </ElTabPane>
        </ElTabs>
    </template>
</template>

<script setup lang="ts">
import { ElButton, ElLink, ElRow, ElTabPane, ElTabs, vLoading } from 'element-plus';
import { computed, ref, watch } from 'vue';
import type { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import '@/styles/text.css';
import PersonalView from '../common/PersonalView.vue';
import Title from '../common/Title.vue';

import AllSummary from './AllSummary.vue';
import Description from './Description.vue';
import PersonalSummary from './PersonalSummary.vue';
import TokenGuide from './TokenGuide.vue';

import { BaseIconClose, BaseIconRefresh } from '@/components/common/icon';
import { httpErrorNotification } from '@/components/Notifications';
import PlayerName from '@/components/PlayerName.vue';
import { downloadTournamentVideos, fetchParticipantList, fetchWeeklyResults } from '@/services/tournamentService';
import { store } from '@/store';
import { LoginStatus } from '@/utils/common/structInterface';
import { streamToZip } from '@/utils/fileIO';
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

const tournament = computed(() => props.tournament);
const token = ref<string>('');
const participant = ref<TournamentParticipant | null>(null);
const result = ref<WeeklyParticipant[]>([]);
const viewedParticipants = ref<WeeklyParticipant[]>([]);
const allSummaryTabPosition = ref(-1);
const loading = ref(false);
const personalViewKey = ref(0);

async function refresh() {
    loading.value = true;
    try {
        if (tournament.value.displayState === TournamentState.Ongoing) {
            result.value = [];
            const participants = await fetchParticipantList(tournament.value.id);
            participant.value = store.login_status === LoginStatus.IsLogin
                ? participants.find((item) => item.user_id === store.user.id) ?? null
                : null;
            token.value = participant.value?.token ?? '';
            personalViewKey.value += 1;
        } else {
            participant.value = null;
            token.value = '';
            result.value = tournament.value.state === TournamentState.Awarded
                ? await fetchWeeklyResults(tournament.value.id)
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

function handleAllSummaryRowClick(row: WeeklyParticipant) {
    if (tournament.value.state !== TournamentState.Awarded || row.user_id === null) return;
    const index = viewedParticipants.value.findIndex((item) => item.id === row.id);
    if (index === -1) {
        viewedParticipants.value.push(row);
        allSummaryTabPosition.value = viewedParticipants.value.length - 1;
    } else {
        allSummaryTabPosition.value = index;
    }
}

function handleAllSummaryTabClose(index: number) {
    viewedParticipants.value.splice(index, 1);
    if (allSummaryTabPosition.value === index) {
        allSummaryTabPosition.value = -1;
    }
}

function downloadAll() {
    downloadTournamentVideos(tournament.value.id).then((data) => {
        void streamToZip(new Uint8Array(data), 'weekly.zip');
    }).catch(httpErrorNotification);
}
</script>
