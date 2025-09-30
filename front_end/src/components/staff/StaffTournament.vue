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
        审核
        <el-button type="success" circle size="small">
            <BaseIconTick />
        </el-button>
        <el-button type="danger" circle size="small">
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
import { ref } from 'vue';
import { httpErrorNotification } from '@/components/Notifications';
import { VCodeBlock } from '@wdns/vue-code-block';
import TournamentStateBadge from '@/views/TournamentView/TournamentStateBadge.vue';
import BaseIconTick from '@/components/common/BaseIconTick.vue';
import BaseIconClose from '@/components/common/BaseIconClose.vue';

const { proxy } = useCurrentInstance();

const tournamentId = ref<number>(0);
const tournament = ref<Tournament | null>(null);

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

</script>
