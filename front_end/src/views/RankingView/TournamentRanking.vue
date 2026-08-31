<template>
    <section class="tournament-ranking">
        <ElTable
            v-loading="loading" :data="rows" :default-sort="defaultSort"
            border table-layout="auto"
            class="ranking-table"
            :empty-text="t('local.empty')"
            @sort-change="handleSortChange"
        >
            <ElTableColumn type="index" :index="(index) => first + index + 1" :label="t('local.rank')" />
            <ElTableColumn :label="t('local.user')">
                <template #default="{ row }">
                    <PlayerName :user-id="row.user_id" />
                </template>
            </ElTableColumn>
            <ElTableColumn :label="t('local.scoreGroup')">
                <ElTableColumn prop="score_current" :label="t('local.scoreCurrent')" sortable="custom" :sort-orders="descendingSortOrders">
                    <template #default="{ row }">
                        {{ formatScoreCurrent(row.score_current, row.last_updated) }}
                    </template>
                </ElTableColumn>
                <ElTableColumn prop="score_total" :label="t('local.scoreTotal')" sortable="custom" :sort-orders="descendingSortOrders" />
            </ElTableColumn>
            <ElTableColumn :label="t('local.gscGroup')">
                <ElTableColumn prop="gsc_total" :label="t('local.gscTotal')" sortable="custom" :sort-orders="descendingSortOrders" />
                <ElTableColumn prop="gsc_best" :label="t('local.gscBest')" sortable="custom" :sort-orders="ascendingSortOrders">
                    <template #default="{ row }">
                        {{ formatGSCBest(row.gsc_best) }}
                    </template>
                </ElTableColumn>
            </ElTableColumn>
            <ElTableColumn :label="t('local.weeklyGroup')">
                <ElTableColumn prop="weekly_total" :label="t('local.weeklyTotal')" sortable="custom" :sort-orders="descendingSortOrders" />
                <ElTableColumn prop="weekly_classic_total" :label="t('local.weeklyClassicTotal')" sortable="custom" :sort-orders="descendingSortOrders" />
                <ElTableColumn prop="weekly_classic_best" :label="t('local.weeklyClassicBest')" sortable="custom" :sort-orders="ascendingSortOrders">
                    <template #default="{ row }">
                        {{ formatWeeklyClassicBest(row.weekly_classic_best) }}
                    </template>
                </ElTableColumn>
            </ElTableColumn>
        </ElTable>

        <ElPagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            class="pagination"
            layout="total, sizes, prev, pager, next, jumper"
            :page-sizes="[20, 50, 100]"
            :total="total"
            @size-change="handlePageSizeChange"
            @current-change="fetchRanking"
        />
    </section>
</template>

<script setup lang="ts">
import { ElPagination, ElTable, ElTableColumn, vLoading } from 'element-plus';
import { computed, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import { httpErrorNotification } from '@/components/Notifications';
import PlayerName from '@/components/PlayerName.vue';
import { fetchTournamentUserRanking, TournamentUserRankFields } from '@/services/tournamentService';
import type { TournamentUserRankField, TournamentUserRankingRow } from '@/services/tournamentService';
import { ms_to_s } from '@/utils';
import { globalNow } from '@/utils/datetime';
import { calculateTournamentScoreCurrent, decodeGSCBest, decodeWeeklyClassicBest } from '@/utils/tournamentUser';

const sortBy = ref<TournamentUserRankField>('score_current');
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);
const rows = ref<TournamentUserRankingRow[]>([]);
const loading = ref(false);
const first = computed(() => (currentPage.value - 1) * pageSize.value);
type ElTableSortOrder = 'ascending' | 'descending';
const ascendingSortOrders: ElTableSortOrder[] = ['ascending'];
const descendingSortOrders: ElTableSortOrder[] = ['descending'];
const defaultSort = { prop: 'score_current', order: 'descending' } as const;

async function fetchRanking() {
    loading.value = true;
    try {
        const data = await fetchTournamentUserRanking({
            sortBy: sortBy.value,
            start: first.value,
            end: first.value + pageSize.value,
        });
        rows.value = data.data;
        total.value = data.total;
    } catch (error) {
        httpErrorNotification(error);
    } finally {
        loading.value = false;
    }
}

function handlePageSizeChange() {
    currentPage.value = 1;
    void fetchRanking();
}

function isTournamentUserRankField(value: unknown): value is TournamentUserRankField {
    return typeof value === 'string' && (TournamentUserRankFields as readonly string[]).includes(value);
}

function handleSortChange({ prop }: { prop: unknown }) {
    if (!isTournamentUserRankField(prop) || prop === sortBy.value) return;
    sortBy.value = prop;
    void fetchRanking();
}

function formatScoreCurrent(scoreCurrent: number, lastUpdated: string): string {
    return calculateTournamentScoreCurrent(scoreCurrent, lastUpdated, globalNow.value).toFixed(2);
}

function formatGSCBest(value: number): string {
    const best = decodeGSCBest(value);
    if (best === undefined) return '-';
    return `${ms_to_s(best.score)} / GSC#${best.order}`;
}

function formatWeeklyClassicBest(value: number): string {
    const best = decodeWeeklyClassicBest(value);
    if (best === undefined) return '-';
    return `${ms_to_s(best.score)} / ${best.year}-W${String(best.week).padStart(2, '0')}`;
}

onMounted(fetchRanking);

const i18nMessages = {
    'zh-cn': { local: {
        empty: '暂无比赛积分排行',
        gscBest: '最佳',
        gscGroup: '金羊杯',
        gscTotal: '总积分',
        scoreGroup: '总分',
        scoreCurrent: '当前积分',
        scoreTotal: '历史总积分',
        weeklyClassicBest: '经典模式最佳',
        weeklyClassicTotal: '经典模式总积分',
        weeklyGroup: '积分赛',
        weeklyTotal: '总积分',
    } },
    en: { local: {
        empty: 'No tournament ranking data',
        gscBest: 'Best',
        gscGroup: 'GSC',
        gscTotal: 'Total',
        scoreGroup: 'Overall',
        scoreCurrent: 'Current',
        scoreTotal: 'History Total',
        weeklyClassicBest: 'Classic Best',
        weeklyClassicTotal: 'Classic Total',
        weeklyGroup: 'Weekly',
        weeklyTotal: 'Total',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>

<style scoped>
.tournament-ranking {
    width: min(1280px, calc(100vw - 32px));
    margin: 0 auto;
}

.ranking-table {
    width: 100%;
}

.pagination {
    justify-content: center;
    margin-top: 16px;
}

@media (max-width: 640px) {
    .tournament-ranking {
        width: calc(100vw - 16px);
    }
}
</style>
