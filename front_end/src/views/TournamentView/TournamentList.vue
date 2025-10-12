<template>
    <el-table :data="tournamentList" @row-click="rowClick">
        <el-table-column :label="t('common.prop.state')">
            <template #default="{row}">
                <TournamentStateIcon :state="row.state" />
            </template>
        </el-table-column>
        <el-table-column :label="t('tournament.tournament')">
            <template #default="{row}">
                {{ row.name }}
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

import { PropType } from 'vue';
import { ElTable, ElTableColumn } from 'element-plus';
import PlayerName from '@/components/PlayerName.vue';
import { toISODateTimeString } from '@/utils/datetime';
import { Tournament } from '@/utils/tournaments';
import { useRouter } from 'vue-router';
import { store } from '@/store';
import TournamentStateIcon from '@/components/widgets/TournamentStateIcon.vue';
import { useI18n } from 'vue-i18n';

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
