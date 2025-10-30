<template>
    <el-table :data="tournamentList" table-layout="auto" @row-click="rowClick">
        <el-table-column :label="t('common.prop.state')">
            <template #default="{row}">
                <TournamentStateIcon :state="row.state" />
            </template>
        </el-table-column>
        <el-table-column :label="t('tournament.tournament')">
            <template #default="{row}: {row: Tournament}">
                {{ row.getLocalName(local.language) }}
            </template>
        </el-table-column>
        <el-table-column :label="t('tournament.host')">
            <template #default="{row}">
                <PlayerName :user-id="row.hostId" :user-name="row.hostName" />
            </template>
        </el-table-column>
        <el-table-column :label="t('tournament.startsFrom')">
            <template #default="{row}">
                {{ row.startDate === undefined ? t('tournament.undecided') : toISODateTimeString(row.startDate) }}
            </template>
        </el-table-column>
        <el-table-column :label="t('tournament.endsBy')">
            <template #default="{row}">
                {{ row.endDate === undefined ? t('tournament.undecided') : toISODateTimeString(row.endDate) }}
            </template>
        </el-table-column>
    </el-table>
</template>

<script setup lang="ts">

import { ElTable, ElTableColumn } from 'element-plus';
import { PropType } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

import PlayerName from '@/components/PlayerName.vue';
import TournamentStateIcon from '@/components/widgets/TournamentStateIcon.vue';
import { local, store } from '@/store';
import { toISODateTimeString } from '@/utils/datetime';
import { Tournament } from '@/utils/tournaments';

const router = useRouter();
const { t } = useI18n();

defineProps({
    tournamentList: {
        type: Array as PropType<Tournament[]>,
        default: () => [],
    },
});

function rowClick(row: Tournament) {
    if (store.tournamentTabs.length === 0) {
        store.tournamentTabs.push(row);
    }
    router.push({ name: 'tournament_id', params: { id: row.id } });
}

</script>
