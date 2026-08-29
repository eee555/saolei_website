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
                    <span class="text">{{ participant.user__realname }}</span>
                    &nbsp;
                    <ElLink underline="never" @click="handleAllSummaryTabClose(index)">
                        <BaseIconClose style="scale: 65%" />
                    </ElLink>
                </template>
                <PersonalView :user-id="participant.user__id" :tournament-id="tournament.id">
                    <template #personalSummary="{ videos }">
                        <GSCPersonalSummary :videos="videos" />
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
import TokenGuide from './TokenGuide.vue';

import { BaseIconClose, BaseIconRefresh } from '@/components/common/icon';
import { httpErrorNotification } from '@/components/Notifications';
import GSCPersonalSummary from '@/components/visualization/GSCPersonalSummary/App.vue';
import { downloadTournamentVideos, fetchGSCResults, fetchParticipantList } from '@/services/tournamentService';
import { store } from '@/store';
import { LoginStatus } from '@/utils/common/structInterface';
import { streamToZip } from '@/utils/fileIO';
import { GSCParticipant } from '@/utils/gsc';
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
const viewedParticipants = ref<GSCParticipant[]>([]);
const allSummaryTabPosition = ref(-1);
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
                ? (await fetchGSCResults(tournament.value.id)).map((value) => new GSCParticipant(value))
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

function handleAllSummaryRowClick(row: GSCParticipant) {
    if (tournament.value.state !== TournamentState.Awarded) return;
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
        void streamToZip(new Uint8Array(data), 'gsc.zip');
    }).catch(httpErrorNotification);
}
</script>
