<template>
    <Title :tournament="tournament" />
    <slot name="description" />
    <template v-if="state === TournamentState.Preparing || state === TournamentState.Ongoing">
        <h3>{{ t('gsc.howToParticipate') }}</h3>
        <slot name="participationGuide" />
    </template>
    <AutoUploader
        v-if="uploadParticipant" v-show="participant && state === TournamentState.Ongoing && autoUploaderEnabled"
        :participant="uploadParticipant" :filter="autoUploaderFilter" :enabled="!!participant && state === TournamentState.Ongoing && autoUploaderEnabled"
        :disabled="personalLoading" @busy="uploadBusy = $event"
    >
        <template #filter>
            <slot name="autoUploaderFilter" />
        </template>
    </AutoUploader>
    <template v-if="state === TournamentState.Awarded || showLiveData">
        <h3 class="tournament-data-heading">
            {{ t('local.data') }}
            <DataExporter v-if="state === TournamentState.Awarded" :key="tournament.id" v-model="allVideos" lazy :fetch-data="getVideos">
                {{ t('local.export') }}
            </DataExporter>
        </h3>
        <AllParticipants v-if="state === TournamentState.Awarded" :key="tournament.id" v-loading="loading" :result="participants">
            <template #allSummary="slotProps">
                <slot name="allSummary" v-bind="slotProps" />
            </template>
            <template #personalSummary="slotProps">
                <slot name="personalSummary" v-bind="slotProps" />
            </template>
        </AllParticipants>
        <ElTabs v-else v-model="selectedTab" data-cy="tournament-data-tabs">
            <ElTabPane name="participants">
                <template #label>
                    <span>{{ t('local.participants') }}</span>
                    <ElButton text circle :title="t('local.refreshParticipants')" :aria-label="t('local.refreshParticipants')" :disabled="loading" data-cy="participants-refresh" @click.stop="refreshParticipants">
                        <BaseIconRefresh />
                    </ElButton>
                </template>
                <slot name="allSummary" :data="participants" :on-participant-select="ignoreSelection" />
            </ElTabPane>
            <ElTabPane v-if="participant" name="personal">
                <template #label>
                    <span>{{ t('gsc.realTimeScore') }}</span>
                    <ElButton text circle :title="t('local.refreshPersonal')" :aria-label="t('local.refreshPersonal')" :disabled="uploadBusy || personalLoading" data-cy="personal-score-refresh" @click.stop="personalView?.refresh()">
                        <BaseIconRefresh />
                    </ElButton>
                </template>
                <PersonalView :key="participant.id" ref="personalView" v-loading="personalLoading" :model-value="participant" :refresh-disabled="uploadBusy" @loading="setPersonalLoading">
                    <template #personalSummary="slotProps">
                        <slot name="personalSummary" v-bind="slotProps" />
                    </template>
                </PersonalView>
            </ElTabPane>
        </ElTabs>
    </template>
</template>

<script setup lang="ts" generic="TParticipant extends TournamentParticipant">
import { ElButton, ElTabPane, ElTabs, vLoading } from 'element-plus';
import { computed, ref, shallowRef, useTemplateRef, watch } from 'vue';
import type { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import AllParticipants from './AllParticipants.vue';
import AutoUploader from './AutoUploader.vue';
import PersonalView from './PersonalView.vue';
import Title from './Title.vue';

import { BaseIconRefresh } from '@/components/common/icon';
import DataExporter from '@/components/widgets/DataExporter.vue';
import { fetchTournamentVideos } from '@/services/tournamentService';
import { globalNow } from '@/utils/datetime';
import type { AnyVideo } from '@/utils/fileIO';
import { TournamentState } from '@/utils/ms_const';
import type { Tournament, TournamentParticipant } from '@/utils/tournaments';
import type { VideoAbstract, VideoAbstractData } from '@/utils/videoabstract';

const props = defineProps({
    tournament: { type: Object as PropType<Tournament>, required: true },
    participants: { type: Array as PropType<TParticipant[]>, required: true },
    index: { type: Number, required: true },
    loading: { type: Boolean, default: false },
    refreshParticipants: { type: Function as PropType<() => Promise<void>>, required: true },
    autoUploaderEnabled: { type: Boolean, default: false },
    autoUploaderFilter: { type: Function as PropType<(video: AnyVideo, stat: VideoAbstract) => boolean>, required: true },
});
defineSlots<{
    description: () => unknown;
    participationGuide: () => unknown;
    autoUploaderFilter: () => unknown;
    allSummary: (props: { data: TParticipant[]; onParticipantSelect: (row: TParticipant) => void }) => unknown;
    personalSummary: (props: { videos: VideoAbstract[] }) => unknown;
}>();
const state = computed(() => props.tournament.getDisplayState(globalNow.value));
const showLiveData = computed(() => state.value === TournamentState.Ongoing || state.value === TournamentState.Finished);
const participant = computed<TParticipant | undefined>(() => props.participants[props.index]);
const uploadParticipant = shallowRef<TParticipant>();
const uploadBusy = ref(false);
const personalLoading = ref(false);
const personalView = useTemplateRef<{ refresh: () => Promise<void> }>('personalView');
const selectedTab = ref('participants');
const allVideos = ref<VideoAbstractData[]>([]);
watch(participant, (value) => {
    if (value) uploadParticipant.value = value;
    else selectedTab.value = 'participants';
}, { immediate: true });
watch(() => participant.value?.id, () => {
    personalLoading.value = false;
}, { flush: 'sync' });
watch(() => props.tournament.id, () => {
    allVideos.value = [];
});

async function getVideos() {
    const { id } = props.tournament;
    const videos = await fetchTournamentVideos(id);
    if (props.tournament.id === id) allVideos.value = videos;
    return videos;
}
function ignoreSelection() {
    // Other participants' replays remain private before awards.
}
function setPersonalLoading(value: boolean, id: number) {
    if (participant.value?.id === id) personalLoading.value = value;
}

const { t } = useI18n({ messages: {
    'zh-cn': { local: { data: '比赛数据', participants: '参赛者', export: '导出所有录像数据', refreshParticipants: '刷新参赛者', refreshPersonal: '刷新个人录像' } },
    en: { local: { data: 'Tournament data', participants: 'Participants', export: 'Export all video stats', refreshParticipants: 'Refresh participants', refreshPersonal: 'Refresh personal videos' } },
} });
</script>

<style scoped>
.tournament-data-heading { display: flex; flex-wrap: wrap; align-items: center; gap: 1rem; }
</style>
