<template>
    <el-table :data="tournamentList" @row-click="rowClick">
        <el-table-column label="状态">
            <template #default="{row}">
                <TournamentStateBadge :state="row.state" />
            </template>
        </el-table-column>
        <el-table-column label="比赛名称">
            <template #default="{row}">
                {{ row.name }}
            </template>
        </el-table-column>
        <el-table-column label="主办方">
            <template #default="{row}">
                <PlayerName :user-id="row.hostId" :user-name="row.hostName" />
            </template>
        </el-table-column>
        <el-table-column label="开始时间">
            <template #default="{row}">
                {{ row.startDate === undefined ? '未定' : toISODateTimeString(row.startDate) }}
            </template>
        </el-table-column>
        <el-table-column label="结束时间">
            <template #default="{row}">
                {{ row.endDate === undefined ? '未定' : toISODateTimeString(row.endDate) }}
            </template>
        </el-table-column>
    </el-table>
</template>

<script setup lang="ts">

import { PropType } from 'vue';
import { ElTable, ElTableColumn } from 'element-plus';
import TournamentStateBadge from './TournamentStateBadge.vue';
import PlayerName from '@/components/PlayerName.vue';
import { toISODateTimeString } from '@/utils/datetime';
import { Tournament } from '@/utils/tournaments';
import { useRouter } from 'vue-router';
import { store } from '@/store';

const router = useRouter();


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
