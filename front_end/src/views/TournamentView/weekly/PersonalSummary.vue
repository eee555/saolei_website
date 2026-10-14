<template>
    <ClassicSummary v-if="tournamentFormat === WeeklyTournamentFormat.Classic" :videos="videos" />
</template>

<script setup lang="ts">
import type { PropType } from 'vue';

import ClassicSummary from '@/components/visualization/WeeklyPersonalSummary/Classic.vue';
import type { VideoAbstract } from '@/utils/videoabstract';
import { WeeklyTournamentFormat } from '@/utils/weekly';

defineProps({
    videos: { type: Array<VideoAbstract>, default: () => [] },
    tournamentFormat: { type: String as PropType<WeeklyTournamentFormat>, default: '' },
});
</script>
