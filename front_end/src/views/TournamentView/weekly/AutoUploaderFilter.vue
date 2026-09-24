<template>
    <ElSelect v-model="filterLevel" size="small" style="width: 250px">
        <ElOption :label="t('local.tournament')" value="tournament" />
        <ElOption :label="t('local.supported')" value="supported" />
        <ElOption :label="t('local.scoreRefreshing')" value="scoreRefreshing" />
    </ElSelect>
</template>

<script setup lang="ts">
import { ElOption, ElSelect } from 'element-plus';
import { ref } from 'vue';
import type { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import type { AnyVideo } from '@/utils/fileIO';
import type { VideoAbstract } from '@/utils/videoabstract';
import type { WeeklyParticipant } from '@/utils/weekly';
import { isWeeklyClassicScoreMode, WeeklyTournamentFormat } from '@/utils/weekly';

const props = defineProps({
    format: { type: String as PropType<WeeklyTournamentFormat>, required: true },
    participant: { type: Object as PropType<WeeklyParticipant | null>, default: null },
});

const filterLevel = ref('supported');

function matchesFilter(video: AnyVideo, stat: VideoAbstract): boolean {
    const { participant } = props;
    if (!participant) return false;
    if (stat.software === 'a' || !participant.token) return false;
    if (!video.race_identifier.split(',').some((identifier) => identifier.trim() === participant.token)) return false;
    if (filterLevel.value === 'tournament') return true;
    if (props.format !== WeeklyTournamentFormat.Classic || !isWeeklyClassicScoreMode(stat.mode)) return false;
    if (stat.level !== 'i' && stat.level !== 'e') return false;
    if (filterLevel.value === 'supported') return true;
    return stat.timems < (stat.level === 'i' ? participant.classic_it[4][1] : participant.classic_et[1][1]);
}

defineExpose({ matchesFilter });

const i18nMessages = {
    'zh-cn': { local: {
        tournament: '所有比赛录像',
        supported: '有效的比赛录像',
        scoreRefreshing: '刷新成绩的比赛录像',
    } },
    en: { local: {
        tournament: 'All tournament videos',
        supported: 'Supported tournament videos',
        scoreRefreshing: 'Score-improving videos',
    } },
};
const { t } = useI18n({ messages: i18nMessages });
</script>
