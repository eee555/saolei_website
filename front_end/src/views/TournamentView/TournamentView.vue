<template>
    <ElTabs v-if="store.tournamentTabs.length === 0" v-model="currentListTab" @tab-change="loadTournamentList">
        <ElTabPane v-for="tab in listTabs" :key="tab.name" :label="t(tab.label)" :name="tab.name" lazy>
            <TournamentList :tournament-list="tournamentLists[tab.name]" />
        </ElTabPane>
    </ElTabs>
    <ElTabs v-else v-model="currentTab" tab-position="left" @tab-remove="tabRemoveHandler" @tab-change="tabChangeHandler">
        <ElTabPane :label="t('tournament.index')" lazy>
            <ElTabs v-model="currentListTab" @tab-change="loadTournamentList">
                <ElTabPane v-for="tab in listTabs" :key="tab.name" :label="t(tab.label)" :name="tab.name" lazy>
                    <TournamentList :tournament-list="tournamentLists[tab.name]" />
                </ElTabPane>
            </ElTabs>
        </ElTabPane>
        <ElTabPane v-for="tournament in store.tournamentTabs" :key="tournament.id">
            <template #label>
                <span>{{ tournament.getLocalName(local.language) }}</span>
            </template>
            <GSCDetail v-if="tournament.subclass === TournamentSubclass.GSC" :id="tournament.id" />
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
import { fetchTournament, fetchTournamentList } from '@/services/tournamentService';
import type { TournamentListCategory } from '@/services/tournamentService';
import { local, store } from '@/store';
import { TournamentSubclass } from '@/utils/ms_const';
import { Tournament } from '@/utils/tournaments';

const { t } = useI18n();

const listTabs: { name: TournamentListCategory; label: string }[] = [
    { name: 'normal', label: 'tournament.listTabs.normal' },
    { name: 'awarded', label: 'tournament.listTabs.awarded' },
    { name: 'other', label: 'tournament.listTabs.other' },
    { name: 'all', label: 'tournament.listTabs.all' },
];
const currentListTab = ref<TournamentListCategory>('normal');
const tournamentLists = ref<Record<TournamentListCategory, Tournament[]>>({
    normal: [],
    awarded: [],
    other: [],
    all: [],
});
const loadedListTabs = ref<Set<TournamentListCategory>>(new Set());

function isTournamentListCategory(value: TabPaneName): value is TournamentListCategory {
    return typeof value === 'string' && listTabs.some((tab) => tab.name === value);
}

function loadTournamentList(tab: TabPaneName = currentListTab.value) {
    if (!isTournamentListCategory(tab)) return;
    if (loadedListTabs.value.has(tab)) return;

    fetchTournamentList(tab).then((data) => {
        tournamentLists.value[tab] = data.map((tournament) => new Tournament(tournament));
        loadedListTabs.value.add(tab);
    }).catch(httpErrorNotification);
}

onMounted(loadTournamentList);

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
        await fetchTournament(newId).then((data) => {
            store.tournamentTabs.push(new Tournament(data));
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
