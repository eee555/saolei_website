<template>
    <ElSelect v-model="filterLevel" size="small" style="width: 250px">
        <ElOption :label="t('local.tournament')" value="tournament" />
        <ElOption :label="t('local.supported')" value="supported" />
        <ElOption :label="t('local.bv')" value="bv" />
    </ElSelect>
</template>

<script setup lang="ts">
import { ElOption, ElSelect } from 'element-plus';
import { ref } from 'vue';
import type { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import type { AnyVideo } from '@/utils/fileIO';
import { isGSCSupportedVideo, meetsGSCBV } from '@/utils/gsc';
import type { TournamentParticipant } from '@/utils/tournaments';
import type { VideoAbstract } from '@/utils/videoabstract';

const props = defineProps({
    participant: { type: Object as PropType<TournamentParticipant | null>, default: null },
});

const filterLevel = ref('bv');

function matchesFilter(video: AnyVideo, stat: VideoAbstract): boolean {
    const { participant } = props;
    if (!participant) return false;
    if (stat.software === 'a') {
        if (!video.player_identifier || video.player_identifier !== participant.arbiter_identifier__identifier) return false;
    } else {
        if (!participant.token || !video.race_identifier.split(',').some((identifier) => identifier.trim() === participant.token)) return false;
    }
    if (filterLevel.value === 'tournament') return true;
    if (!isGSCSupportedVideo(stat)) return false;
    if (filterLevel.value === 'supported') return true;
    return meetsGSCBV(stat);
}

defineExpose({ matchesFilter });

const i18nMessages = {
    'zh-cn': { local: {
        tournament: '所有比赛录像',
        supported: '级别和模式符合',
        bv: '3BV 下限符合',
    } },
    en: { local: {
        tournament: 'All tournament videos',
        supported: 'Supported levels and modes',
        bv: '3BV minimum met',
    } },
};
const { t } = useI18n({ messages: i18nMessages });
</script>
