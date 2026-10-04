<template>
    比赛ID
    &nbsp;
    <ElInputNumber v-model="tournamentId" :min="0" :controls="false" />
    &nbsp;
    <BaseButton @click="refreshTournamentInfo">
        查询
    </BaseButton>
    <br>
    <template v-if="tournament">
        状态
        &nbsp;
        <TournamentStateIcon :state="tournament.getDisplayState(globalNow)" />
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
        <BaseButton class="square-button" type="success" size="small" aria-label="通过审核" :disabled="!tournament.canValidate" @click="validateTournament(true)">
            <BaseIconTick />
        </BaseButton>
        <BaseButton class="square-button" type="danger" size="small" aria-label="取消审核" :disabled="!tournament.canInvalidate" @click="validateTournament(false)">
            <BaseIconClose />
        </BaseButton>
        <br>
        名称
        <VCodeBlock v-if="tournament" :code="JSON.stringify(tournament.name)" lang="json" highlightjs />
        描述
        <VCodeBlock v-if="tournament.description" :code="JSON.stringify(tournament.description)" lang="json" highlightjs />
    </template>
</template>

<script setup lang="ts">
import { VCodeBlock } from '@wdns/vue-code-block';
import { ElInputNumber } from 'element-plus';
import { ref } from 'vue';

import BaseButton from '@/components/common/BaseButton.vue';
import { BaseIconClose, BaseIconTick } from '@/components/common/icon';
import { httpErrorNotification, successNotification } from '@/components/Notifications';
import TournamentStateIcon from '@/components/widgets/TournamentStateIcon.vue';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { globalNow } from '@/utils/datetime';
import { Tournament } from '@/utils/tournaments';

const { proxy } = useCurrentInstance();

const tournamentId = ref<number>(0);
const tournament = ref<Tournament | null>(null);

type LocalizedString = string | Partial<Record<string, string>>;

interface TournamentResponseData {
    [key: string]: unknown;
    id?: number;
    name?: LocalizedString;
    description?: LocalizedString;
    start_time?: string | Date | null;
    end_time?: string | Date | null;
    subclass?: ConstructorParameters<typeof Tournament>[0]['subclass'];
    data?: ConstructorParameters<typeof Tournament>[0]['data'];
    host_id?: number;
    state?: ConstructorParameters<typeof Tournament>[0]['state'];
}

function refreshTournamentInfo() {
    if (!tournamentId.value) {
        tournament.value = null;
        return;
    }
    proxy.$axios.get<TournamentResponseData>('/api/tournament/get', { params: { tournament_id: tournamentId.value } }).then(({ data }) => {
        tournament.value = new Tournament(data);
    }).catch((e: unknown) => {
        tournament.value = null;
        httpErrorNotification(e);
    });
}

function validateTournament(valid: boolean) {
    if (!tournamentId.value) return;
    proxy.$axios.post('/api/tournament/validate', {
        id: tournamentId.value,
        valid: valid,
    }).then((response) => {
        refreshTournamentInfo();
        successNotification(response);
    }).catch(httpErrorNotification);
}
</script>
