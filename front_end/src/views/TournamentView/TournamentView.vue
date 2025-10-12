<template>
    <TournamentList v-if="store.tournamentTabs.length === 0" :tournament-list="tournamentList" />
    <el-tabs v-else v-model="currentTab" tab-position="left" @tab-remove="tabRemoveHandler" @tab-change="tabChangeHandler">
        <el-tab-pane :label="t('tournament.index')" lazy>
            <TournamentList :tournament-list="tournamentList" />
        </el-tab-pane>
        <el-tab-pane v-for="tournament in store.tournamentTabs" :key="tournament.id">
            <template #label>
                <span>{{ tournament.getLocalName(local.language) }}</span>
            </template>
            <GSCDetail v-if="tournament.series === TournamentSeries.GSC" :id="tournament.id" />
            <TournamentDetail v-else :tournament="tournament" />
        </el-tab-pane>
    </el-tabs>
</template>

<script setup lang="ts">
import { httpErrorNotification } from '@/components/Notifications';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { onMounted, ref, watch } from 'vue';
import TournamentList from './TournamentList.vue';
import { Tournament } from '@/utils/tournaments';
import { store, local } from '@/store';
import { TabPaneName, ElTabs, ElTabPane } from 'element-plus';
import { useRoute, useRouter } from 'vue-router';
import TournamentDetail from './TournamentDetail.vue';
import GSCDetail from './GSCDetail.vue';
import { TournamentSeries } from '@/utils/ms_const';
import { useI18n } from 'vue-i18n';

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
    if (newId === undefined) {
        currentTab.value = '0';
        return;
    }
    const tabIndex = store.tournamentTabs.findIndex((t) => t.id === Number(newId));
    if (tabIndex === -1) {
        await proxy.$axios.get('tournament/get/', {
            params: {
                id: newId,
            },
        }).then((response) => {
            store.tournamentTabs.push(new Tournament(response.data.data));
        }).catch(httpErrorNotification);
        currentTab.value = (store.tournamentTabs.length).toString();
    } else {
        currentTab.value = (tabIndex + 1).toString();
    }
}, { immediate: true });

// watch(currentTab, (v) => {
//     console.log(v);
// }, { immediate: true });

function tabRemoveHandler(tabIndex: TabPaneName) {
    console.log(tabIndex);
    tabIndex = Number(tabIndex) - 1;
    store.tournamentTabs.splice(tabIndex as number, 1);
    if (tabIndex === 0) {
        router.push({ name: 'tournament' });
    } else {
        router.push({ name: 'tournament_id', params: { id: store.tournamentTabs[tabIndex - 1].id } });
    }
}

function tabChangeHandler(tabIndex: TabPaneName) {
    if (tabIndex === '0') {
        router.push({ name: 'tournament' });
        return;
    }
    router.push({ name: 'tournament_id', params: { id: store.tournamentTabs[tabIndex as number - 1].id } });
}

</script>
