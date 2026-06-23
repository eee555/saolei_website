<template>
    <TournamentList v-if="store.tournamentTabs.length === 0" :tournament-list="tournamentList" />
    <ElTabs v-else v-model="currentTab" tab-position="left" @tab-remove="tabRemoveHandler" @tab-change="tabChangeHandler">
        <ElTabPane :label="t('tournament.index')" lazy>
            <TournamentList :tournament-list="tournamentList" />
        </ElTabPane>
        <ElTabPane v-for="tournament in store.tournamentTabs" :key="tournament.id">
            <template #label>
                <span>{{ tournament.getLocalName(local.language) }}</span>
            </template>
            <GSCDetail v-if="tournament.series === TournamentSeries.GSC" :id="tournament.id" />
            <TournamentDetail v-else :tournament="tournament" />
        </ElTabPane>
    </ElTabs>
</template>

<script setup lang="ts">
import type { TabPaneName } from 'element-plus';
import { ElTabPane, ElTabs } from 'element-plus';
import { onMounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';

import GSCDetail from './GSCDetail.vue';
import TournamentDetail from './TournamentDetail.vue';
import TournamentList from './TournamentList.vue';

import { httpErrorNotification } from '@/components/Notifications';
import { local, store } from '@/store';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { TournamentSeries } from '@/utils/ms_const';
import { Tournament } from '@/utils/tournaments';

const { proxy } = useCurrentInstance();
const { t } = useI18n();

const tournamentList = ref<Tournament[]>([]);

function getTournaments() {
    proxy.$axios.get('tournament/get_list/').then((response) => {
        for (const tournament of response.data.data) {
            tournamentList.value.push(new Tournament(tournament));
        }
    }).catch(httpErrorNotification);
}

onMounted(getTournaments);

const router = useRouter();
const route = useRoute();

const currentTab = ref<TabPaneName>('0');

watch(() => route.params.id, async (newId) => {
    if (typeof newId !== 'string') {
        currentTab.value = '0';
        return;
    }

    const tabIndex = store.tournamentTabs.findIndex((tab) => tab.id === Number(newId));
    if (tabIndex === -1) {
        await proxy.$axios.get('tournament/get/', {
            params: {
                id: newId,
            },
        }).then((response) => {
            store.tournamentTabs.push(new Tournament(response.data.data));
        }).catch(httpErrorNotification);
        currentTab.value = store.tournamentTabs.length.toString();
    } else {
        currentTab.value = (tabIndex + 1).toString();
    }
}, { immediate: true });

// watch(currentTab, (v) => {
//     console.log(v);
// }, { immediate: true });

function tabRemoveHandler(tabIndex: TabPaneName) {
    tabIndex = Number(tabIndex) - 1;
    store.tournamentTabs.splice(tabIndex, 1);
    if (tabIndex === 0) {
        void router.push({ name: 'tournament' });
    } else {
        void router.push({ name: 'tournament_id', params: { id: store.tournamentTabs[tabIndex - 1].id } });
    }
}

function tabChangeHandler(tabIndex: TabPaneName) {
    if (tabIndex === '0') {
        void router.push({ name: 'tournament' });
        return;
    }
    void router.push({ name: 'tournament_id', params: { id: store.tournamentTabs[tabIndex as number - 1].id } });
}
</script>
