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
        <GSCPersonalView :user-id="store.user.id" :tournament-id="tournament.id" />
    </template>
    <template v-if="[TournamentState.Finished, TournamentState.Awarded].includes(tournament.state)">
        <h3>
            {{ t('gsc.finalResults') }}
        </h3>
        <el-tabs v-model="allSummaryTabPosition">
            <el-tab-pane :label="t('tournament.ranking')" lazy :name="-1">
                <GSCAllSummary :data="result" @row-click="handleAllSummaryRowClick" />
            </el-tab-pane>
            <el-tab-pane v-for="(participant, index) in viewedParticipants" :key="participant.id" lazy :name="index">
                <template #label>
                    <el-text>{{ participant.user__realname }}</el-text>
                    &nbsp;
                    <el-link :underline="false" @click="handleAllSummaryTabClose(index)">
                        <base-icon-close style="scale: 65%" />
                    </el-link>
                </template>
                <GSCPersonalView :user-id="participant.user__id" :tournament-id="tournament.id" />
            </el-tab-pane>
        </el-tabs>
    </template>
</template>

<script setup lang="ts">

import { httpErrorNotification } from '@/components/Notifications';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { Tournament } from '@/utils/tournaments';
import { ElText, ElTabs, ElTabPane, ElLink } from 'element-plus';
import { ref, watch } from 'vue';
import { store } from '@/store';
import { LoginStatus } from '@/utils/common/structInterface';
import { TournamentState } from '@/utils/ms_const';
import { GSCParticipant } from '@/utils/gsc';
import GSCTokenGuide from './GSCTokenGuide.vue';
import BaseIconRefresh from '@/components/common/BaseIconRefresh.vue';
import GSCAllSummary from './GSCAllSummary.vue';
import { useI18n } from 'vue-i18n';
import TournamentStateIcon from '@/components/widgets/TournamentStateIcon.vue';
import GSCPersonalView from './GSCPersonalView.vue';
import BaseIconClose from '@/components/common/BaseIconClose.vue';

const props = defineProps({
    id: {
        type: Number,
        required: true,
    },
});

const { proxy } = useCurrentInstance();
const { t } = useI18n();

const tournament = ref<Tournament>(new Tournament({}));
const order = ref<number>(0);
const token = ref<string>('');
const result = ref<GSCParticipant[]>([]);
const personaltoken = ref<string>('');
const viewedParticipants = ref<GSCParticipant[]>([]);
const allSummaryTabPosition = ref(-1);

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
        } else {
            personaltoken.value = '';
            result.value = response.data.results;
        }
    }).catch(httpErrorNotification);
}

watch(() => props.id, refresh, { immediate: true });

function handleAllSummaryRowClick(row: GSCParticipant) {
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

</script>
