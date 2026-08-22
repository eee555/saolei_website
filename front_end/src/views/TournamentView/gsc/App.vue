<template>
    <h1>
        {{ t('gsc.title', { order: order }) }}
        <TournamentStateIcon :state="tournament.displayState" />
    </h1>
    {{ t('gsc.schedule') }}{{ t('common.punct.colon') }}
    <span class="text">
        {{ tournament.displayStartTime() }}
        &nbsp;~&nbsp;
        {{ tournament.displayEndTime() }}
    </span>
    &nbsp;
    <br>
    {{ t('gsc.description.line1') }}
    <br>
    {{ t('gsc.description.line2') }}
    <br>
    <template v-if="([TournamentState.Preparing, TournamentState.Ongoing] as TournamentState[]).includes(tournament.displayState)">
        <h3>{{ t('gsc.howToParticipate') }}</h3>
        <GSCTokenGuide
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
        <GSCPersonalView v-loading="loading" :user-id="store.user.id" :tournament-id="tournament.id" />
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
                <GSCAllSummary :data="result" @row-click="handleAllSummaryRowClick" />
            </ElTabPane>
            <ElTabPane v-for="(participant, index) in viewedParticipants" :key="participant.id" lazy :name="index">
                <template #label>
                    <span class="text">{{ participant.user__realname }}</span>
                    &nbsp;
                    <ElLink underline="never" @click="handleAllSummaryTabClose(index)">
                        <BaseIconClose style="scale: 65%" />
                    </ElLink>
                </template>
                <GSCPersonalView :user-id="participant.user__id" :tournament-id="tournament.id" />
            </ElTabPane>
        </ElTabs>
    </template>
</template>

<script setup lang="ts">
import { ElButton, ElLink, ElRow, ElTabPane, ElTabs, vLoading } from 'element-plus';
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import '@/styles/text.css';
import GSCAllSummary from './GSCAllSummary.vue';
import GSCPersonalView from './GSCPersonalView.vue';
import GSCTokenGuide from './GSCTokenGuide.vue';

import { BaseIconClose, BaseIconRefresh } from '@/components/common/icon';
import { httpErrorNotification } from '@/components/Notifications';
import TournamentStateIcon from '@/components/widgets/TournamentStateIcon.vue';
import { downloadTournamentVideos, fetchGSCInfo } from '@/services/tournamentService';
import { store } from '@/store';
import { LoginStatus } from '@/utils/common/structInterface';
import { streamToZip } from '@/utils/fileIO';
import { GSCParticipant } from '@/utils/gsc';
import { TournamentState } from '@/utils/ms_const';
import { Tournament } from '@/utils/tournaments';

const props = defineProps({
    id: {
        type: Number,
        required: true,
    },
});

const { t } = useI18n();

const tournament = ref<Tournament>(new Tournament({}));
const order = ref<number>(0);
const token = ref<string>('');
const result = ref<GSCParticipant[]>([]);
const personaltoken = ref<string>('');
const participant = ref(false);
const viewedParticipants = ref<GSCParticipant[]>([]);
const allSummaryTabPosition = ref(-1);
const loading = ref(false);

async function refresh() {
    loading.value = true;
    await fetchGSCInfo(props.id).then((response) => {
        tournament.value = new Tournament(response.data);
        order.value = response.data.order;
        token.value = response.data.token;

        if (tournament.value.displayState === TournamentState.Ongoing && store.login_status === LoginStatus.IsLogin) {
            result.value = [];
            participant.value = response.participant;
            personaltoken.value = response.identifier ?? '';
        } else {
            participant.value = false;
            personaltoken.value = '';
            result.value = (response.results ?? []).map((value) => new GSCParticipant(value));
        }
    }).catch(httpErrorNotification);
    loading.value = false;
}

watch(() => props.id, refresh, { immediate: true });

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
