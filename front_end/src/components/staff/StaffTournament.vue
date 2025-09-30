<template>
    比赛ID
    &nbsp;
    <el-input-number v-model="tournamentId" :min="0" :controls="false" />
    &nbsp;
    <el-button @click="refreshTournamentInfo">
        查询
    </el-button>
    <br>
    <template v-if="tournament">
        状态
        &nbsp;
        <TournamentStateBadge :state="tournament.state" />
        <br>
        开始时间
        &nbsp;
        {{ tournament.startDate }}
        <br>
        结束时间
        &nbsp;
        {{ tournament.endDate }}
        <br>
        审核
        <el-button type="success" circle size="small" :disabled="!canValidate" @click="validateTournament(true)">
            <BaseIconTick />
        </el-button>
        <el-button type="danger" circle size="small" :disabled="!canInvalidate" @click="validateTournament(false)">
            <BaseIconClose />
        </el-button>
        <br>
        名称
        <v-code-block v-if="tournament" :code="tournament.name" lang="javascript" prismjs />
        描述
        <v-code-block v-if="tournament.description" :code="tournament.description" lang="javascript" prismjs />
    </template>
</template>

<script setup lang="ts">

import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { Tournament } from '@/utils/tournaments';
import { ElInputNumber, ElButton } from 'element-plus';
import { computed, ref } from 'vue';
import { httpErrorNotification, successNotification } from '@/components/Notifications';
import { VCodeBlock } from '@wdns/vue-code-block';
import TournamentStateBadge from '@/views/TournamentView/TournamentStateBadge.vue';
import BaseIconTick from '@/components/common/BaseIconTick.vue';
import BaseIconClose from '@/components/common/BaseIconClose.vue';
import { TournamentState } from '@/utils/ms_const';

const { proxy } = useCurrentInstance();

const tournamentId = ref<number>(0);
const tournament = ref<Tournament | null>(null);

const canValidate = computed(() => {
    if (!tournament.value) return false;
    if ([TournamentState.Awarded, TournamentState.Finished, TournamentState.Ongoing, TournamentState.Preparing].includes(tournament.value.state)) return false;
    if (!tournament.value.startDate || !tournament.value.endDate || tournament.value.startDate >= tournament.value.endDate) return false;
    return true;
});

const canInvalidate = computed(() => {
    if (!tournament.value) return false;
    if ([TournamentState.Awarded, TournamentState.Cancelled].includes(tournament.value.state)) return false;
    return true;
})

function refreshTournamentInfo() {
    if (!tournamentId.value) {
        tournament.value = null;
        return;
    }
    proxy.$axios.get('tournament/get/', { params: { id: tournamentId.value } }).then((response: any) => {
        tournament.value = new Tournament(response.data.data);
    }).catch((e: any) => {
        tournament.value = null;
        httpErrorNotification(e);
    });
}

function validateTournament(valid: boolean) {
    if (!tournamentId.value) return;
    proxy.$axios.post('tournament/validate/', {
        id: tournamentId.value,
        valid: valid,
    }).then((response) => {
        refreshTournamentInfo();
        successNotification(response);
    }).catch(httpErrorNotification);
}

</script>
