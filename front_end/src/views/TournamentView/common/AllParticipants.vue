<template>
    <ElTabs v-model="selectedTab" data-cy="all-participants-tabs">
        <ElTabPane :label="t('local.ranking')" lazy :name="rankingTabName">
            <DataExporter v-model="allVideos" lazy :fetch-data="getVideos">
                {{ t('local.exportVideoStat') }}
            </DataExporter>
            <ElRow style="height: 0.5em" />
            <slot name="allSummary" :data="result" :on-participant-select="handleAllSummaryRowClick" />
        </ElTabPane>
        <ElTabPane v-for="participant in viewedParticipants" :key="participant.id" lazy :name="participant.id">
            <template #label>
                <PlayerName v-if="participant.user_id !== null" :user-id="participant.user_id" />
                &nbsp;
                <ElLink data-cy="all-participants-tab-close" underline="never" @click.stop="handleAllSummaryTabClose(participant.id)">
                    <BaseIconClose style="scale: 65%" />
                </ElLink>
            </template>
            <PersonalView v-if="participant.user_id !== null" :user-id="participant.user_id" :tournament-id="tournament.id">
                <template #personalSummary="{ videos }">
                    <slot name="personalSummary" :videos="videos" />
                </template>
            </PersonalView>
        </ElTabPane>
    </ElTabs>
</template>

<script setup lang="ts" generic="TParticipant extends { id: number; user_id: number | null }">
import { ElLink, ElRow, ElTabPane, ElTabs } from 'element-plus';
import { ref, shallowRef } from 'vue';
import type { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import PersonalView from './PersonalView.vue';

import { BaseIconClose } from '@/components/common/icon';
import PlayerName from '@/components/PlayerName.vue';
import DataExporter from '@/components/widgets/DataExporter.vue';
import { fetchTournamentVideos } from '@/services/tournamentService';
import type { Tournament } from '@/utils/tournaments';
import type { VideoAbstract, VideoAbstractData } from '@/utils/videoabstract';

const props = defineProps({
    tournament: { type: Object as PropType<Tournament>, required: true },
    result: { type: Array as PropType<TParticipant[]>, default: () => [] },
});

defineSlots<{
    allSummary: (props: { data: TParticipant[]; onParticipantSelect: (row: TParticipant) => void }) => unknown;
    personalSummary: (props: { videos: VideoAbstract[] }) => unknown;
}>();

const rankingTabName = -1;
const selectedTab = ref(rankingTabName);
const viewedParticipants = shallowRef<TParticipant[]>([]);
const allVideos = ref<VideoAbstractData[]>([]);

function handleAllSummaryRowClick(row: TParticipant) {
    if (row.user_id === null || row.user_id === 0) return;
    const index = viewedParticipants.value.findIndex((item) => item.id === row.id);
    if (index === -1) {
        viewedParticipants.value = [...viewedParticipants.value, row];
    }
    selectedTab.value = row.id;
}

function handleAllSummaryTabClose(participantId: number) {
    viewedParticipants.value = viewedParticipants.value.filter((participant) => participant.id !== participantId);
    if (selectedTab.value === participantId) {
        selectedTab.value = rankingTabName;
    }
}

async function getVideos(): Promise<VideoAbstractData[]> {
    if (props.tournament.id === 0) return [];
    allVideos.value = await fetchTournamentVideos(props.tournament.id);
    return allVideos.value;
}

const i18nMessages = {
    'zh-cn': { local: {
        exportVideoStat: '导出所有录像数据',
        ranking: '排名',
    } },
    en: { local: {
        exportVideoStat: 'Export all video stats',
        ranking: 'Ranking',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>
