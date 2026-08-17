<template>
    <h1>
        {{ tournament.getLocalName(local.language) }}
        <TournamentStateIcon :state="tournament.displayState" />
    </h1>
    {{ t('gsc.schedule') }}{{ t('common.punct.colon') }}
    <span class="text">
        {{ tournament.displayStartTime() }}
        &nbsp;~&nbsp;
        {{ tournament.displayEndTime() }}
    </span>
    <br>
    <template v-if="([TournamentState.Preparing, TournamentState.Ongoing] as TournamentState[]).includes(tournament.displayState)">
        <h3>{{ t('gsc.howToParticipate') }}</h3>
        <TokenGuide
            v-model:token="token"
            :registration-open="tournament.displayState === TournamentState.Ongoing"
            :tournament-id="tournament.id"
            @refresh="refresh"
        />
    </template>
    <template v-if="tournament.displayState === TournamentState.Ongoing && store.login_status === LoginStatus.IsLogin">
        <h3>
            {{ t('gsc.realTimeScore') }}&nbsp;
            <ElLink underline="never" :disabled="loading">
                <BaseIconRefresh @click="refresh" />
            </ElLink>
        </h3>
        <PersonalView v-loading="loading" :user-id="store.user.id" :tournament-id="tournament.id" />
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
                <PersonalView v-if="participant.user_id !== null" :user-id="participant.user_id" :tournament-id="tournament.id" />
            </ElTabPane>
        </ElTabs>
    </template>
</template>

<script setup lang="ts">
import { ElButton, ElLink, ElRow, ElTabPane, ElTabs, vLoading } from 'element-plus';
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import '@/styles/text.css';
import AllSummary from './AllSummary.vue';
import PersonalView from './PersonalView.vue';
import TokenGuide from './TokenGuide.vue';

import { BaseIconClose, BaseIconRefresh } from '@/components/common/icon';
import { httpErrorNotification } from '@/components/Notifications';
import PlayerName from '@/components/PlayerName.vue';
import TournamentStateIcon from '@/components/widgets/TournamentStateIcon.vue';
import { downloadTournamentVideos, fetchWeeklyInfo } from '@/services/tournamentService';
import { local, store } from '@/store';
import { LoginStatus } from '@/utils/common/structInterface';
import { streamToZip } from '@/utils/fileIO';
import { TournamentState, TournamentSubclass } from '@/utils/ms_const';
import { Tournament } from '@/utils/tournaments';
import { WeeklyParticipant } from '@/utils/weekly';

const props = defineProps({
    id: {
        type: Number,
        required: true,
    },
});

const { t } = useI18n();

const tournament = ref<Tournament>(new Tournament({}));
const token = ref<string>('');
const result = ref<WeeklyParticipant[]>([]);
const viewedParticipants = ref<WeeklyParticipant[]>([]);
const allSummaryTabPosition = ref(-1);
const loading = ref(false);

async function refresh() {
    loading.value = true;
    await fetchWeeklyInfo(props.id).then((response) => {
        tournament.value = new Tournament({
            ...response.data,
            subclass: TournamentSubclass.Weekly,
            data: {
                year: response.data.year,
                week: response.data.week,
                tournament_format: response.data.tournament_format,
            },
        });
        token.value = response.token ?? '';

        if (tournament.value.displayState === TournamentState.Ongoing && store.login_status === LoginStatus.IsLogin) {
            result.value = [];
        } else {
            result.value = (response.results ?? []).map((value) => new WeeklyParticipant(value));
        }
    }).catch(httpErrorNotification);
    loading.value = false;
}

watch(() => props.id, refresh, { immediate: true });

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
