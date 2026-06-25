<template>
    <!-- @vue-generic {Tournament} -->
    <ElTable :data="tournamentList" table-layout="auto" :default-sort="{ prop: 'startDate', order: 'descending' }" @row-click="rowClick">
        <ElTableColumn :label="t('common.prop.state')">
            <template #default="{row}">
                <TournamentStateIcon :state="row.state" />
            </template>
        </ElTableColumn>
        <ElTableColumn :label="t('tournament.tournament')">
            <template #default="{row}">
                {{ row.getLocalName(local.language) }}
            </template>
        </ElTableColumn>
        <ElTableColumn :label="t('tournament.host')">
            <template #default="{row}">
                <PlayerName :user-id="row.hostId" />
            </template>
        </ElTableColumn>
        <ElTableColumn prop="startDate" :label="t('tournament.startsFrom')" sortable>
            <template #default="{row}">
                {{ row.startDate === undefined ? t('tournament.undecided') : toISODateTimeString(row.startDate) }}
            </template>
        </ElTableColumn>
        <ElTableColumn prop="endDate" :label="t('tournament.endsBy')" sortable>
            <template #default="{row}">
                {{ row.endDate === undefined ? t('tournament.undecided') : toISODateTimeString(row.endDate) }}
            </template>
        </ElTableColumn>
    </ElTable>
</template>

<script setup lang="ts">
import { ElTable, ElTableColumn } from 'element-plus';
import type { PropType } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

import PlayerName from '@/components/PlayerName.vue';
import TournamentStateIcon from '@/components/widgets/TournamentStateIcon.vue';
import { local, store } from '@/store';
import { toISODateTimeString } from '@/utils/datetime';
import type { Tournament } from '@/utils/tournaments';

defineProps({
    tournamentList: {
        type: Array as PropType<Tournament[]>,
        default: () => [],
    },
});
const router = useRouter();
const { t } = useI18n();

function rowClick(row: Tournament) {
    if (store.tournamentTabs.length === 0) {
        store.tournamentTabs.push(row);
    }
    void router.push({ name: 'tournament_id', params: { id: row.id } });
}
</script>
