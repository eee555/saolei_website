<template>
    <TournamentList :tournament-list="tournamentList" />
</template>

<script setup lang="ts">
import { httpErrorNotification } from '@/components/Notifications';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { onMounted, ref } from 'vue';
import TournamentList from './TournamentList.vue';
import { Tournament } from '@/utils/tournaments';

const { proxy } = useCurrentInstance();

const tournamentList = ref<Tournament[]>([]);

function getTournaments() {
    proxy.$axios.get('tournament/get_list/').then((response) => {
        for (const tournament of response.data) {
            tournamentList.value.push({
                id: tournament.id,
                name: tournament.name,
                startDate: new Date(tournament.start_time),
                endDate: new Date(tournament.end_time),
                hostId: tournament.host__id,
                hostName: tournament.host__realname,
                state: tournament.state,
            });
        }
    }).catch(httpErrorNotification);
}

onMounted(getTournaments);

</script>
