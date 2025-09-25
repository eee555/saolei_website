<template>
    <el-table :data="tournamentList">
        <el-table-column label="状态">
            <template #default="{row}">
                <TournamentStateBadge :state="row.state" />
            </template>
        </el-table-column>
        <el-table-column label="">
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
                {{ toISODateTimeString(row.startDate) }}
            </template>
        </el-table-column>
        <el-table-column label="结束时间">
            <template #default="{row}">
                {{ toISODateTimeString(row.endDate) }}
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

defineProps({
    tournamentList: {
        type: Array as PropType<Tournament[]>,
        default: () => [],
    },
});

</script>
