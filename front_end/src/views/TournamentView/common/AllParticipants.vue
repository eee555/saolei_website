<template>
    <ElTabs v-model="selectedTab" data-cy="all-participants-tabs">
        <ElTabPane :label="t('local.ranking')" lazy :name="rankingTabName">
            <slot name="allSummary" :data="result" :on-participant-select="handleAllSummaryRowClick" />
        </ElTabPane>
        <ElTabPane v-for="participant in viewedParticipants" :key="participant.id" lazy :name="participant.id">
            <template #label>
                <PlayerName v-if="participant.user_id !== 0" :user-id="participant.user_id" :interactive="false" />
                &nbsp;
                <ElLink data-cy="all-participants-tab-close" underline="never" @click.stop="handleAllSummaryTabClose(participant.id)">
                    <BaseIconClose style="scale: 65%" />
                </ElLink>
            </template>
            <PersonalView v-if="participant.user_id !== 0" :model-value="participant">
                <template #personalSummary="{ videos }">
                    <slot name="personalSummary" :videos="videos" />
                </template>
            </PersonalView>
        </ElTabPane>
    </ElTabs>
</template>

<script setup lang="ts" generic="TParticipant extends TournamentParticipant">
import { ElLink, ElTabPane, ElTabs } from 'element-plus';
import { ref, shallowRef } from 'vue';
import type { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import PersonalView from './PersonalView.vue';

import { BaseIconClose } from '@/components/common/icon';
import PlayerName from '@/components/PlayerName.vue';
import type { TournamentParticipant } from '@/utils/tournaments';
import type { VideoAbstract } from '@/utils/videoabstract';

defineProps({
    result: { type: Array as PropType<TParticipant[]>, default: () => [] },
});

defineSlots<{
    allSummary: (props: { data: TParticipant[]; onParticipantSelect: (row: TParticipant) => void }) => unknown;
    personalSummary: (props: { videos: VideoAbstract[] }) => unknown;
}>();

const rankingTabName = -1;
const selectedTab = ref(rankingTabName);
const viewedParticipants = shallowRef<TParticipant[]>([]);

function handleAllSummaryRowClick(row: TParticipant) {
    if (row.user_id === 0) return;
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

const i18nMessages = {
    'zh-cn': { local: {
        ranking: '排名',
    } },
    en: { local: {
        ranking: 'Ranking',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>
