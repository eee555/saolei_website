<template>
    <section class="tournament-ranking">
        <BaseTable
            v-loading="loading" :empty="rows.length === 0" :column-count="9"
            class="ranking-table"
            :empty-text="t('local.empty')"
        >
            <template #head>
                <tr>
                    <th scope="col" rowspan="2" class="table-col-rank" />
                    <th scope="col" rowspan="2" class="table-col-player" />
                    <th scope="colgroup" colspan="2" class="table-col-center">
                        {{ t('local.scoreGroup') }}
                    </th>
                    <th scope="colgroup" colspan="2" class="table-col-center">
                        {{ t('local.gscGroup') }}
                    </th>
                    <th scope="colgroup" colspan="3" class="table-col-center">
                        {{ t('local.weeklyGroup') }}
                    </th>
                </tr>
                <tr>
                    <th v-for="column in rankColumns" :key="column.field" scope="col" class="table-col-number">
                        <BaseTextButton
                            class="rank-header-button" :data-sort-field="column.field"
                            :type="sortBy === column.field ? 'primary' : 'default'" :aria-pressed="sortBy === column.field"
                            :aria-label="`${t(`local.${column.group}`)} ${t(`local.${column.label}`)}`"
                            @click="selectSort(column.field)"
                        >
                            {{ t(`local.${column.label}`) }}
                        </BaseTextButton>
                    </th>
                </tr>
            </template>
            <tr v-for="(row, index) in rows" :key="row.user_id">
                <td class="table-col-rank">
                    {{ first + index + 1 }}
                </td>
                <td class="table-col-player">
                    <PlayerName :user-id="row.user_id" />
                </td>
                <td class="table-col-number">
                    {{ formatScoreCurrent(row.score_current, row.last_updated) }}
                </td>
                <td class="table-col-number">
                    {{ row.score_total }}
                </td>
                <td class="table-col-number">
                    {{ row.gsc_total }}
                </td>
                <td class="table-col-number">
                    {{ formatGSCBest(row.gsc_best) }}
                </td>
                <td class="table-col-number">
                    {{ row.weekly_total }}
                </td>
                <td class="table-col-number">
                    {{ row.weekly_classic_total }}
                </td>
                <td class="table-col-number">
                    {{ formatWeeklyClassicBest(row.weekly_classic_best) }}
                </td>
            </tr>
        </BaseTable>

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
import { ElPagination, vLoading } from 'element-plus';
import { computed, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import BaseTable from '@/components/common/BaseTable.vue';
import BaseTextButton from '@/components/common/BaseTextButton.vue';
import { httpErrorNotification } from '@/components/Notifications';
import PlayerName from '@/components/PlayerName.vue';
import { fetchTournamentUserRanking } from '@/services/tournamentService';
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
const rankColumns = [
    { field: 'score_current', group: 'scoreGroup', label: 'scoreCurrent' },
    { field: 'score_total', group: 'scoreGroup', label: 'scoreTotal' },
    { field: 'gsc_total', group: 'gscGroup', label: 'gscTotal' },
    { field: 'gsc_best', group: 'gscGroup', label: 'gscBest' },
    { field: 'weekly_total', group: 'weeklyGroup', label: 'weeklyTotal' },
    { field: 'weekly_classic_total', group: 'weeklyGroup', label: 'weeklyClassicTotal' },
    { field: 'weekly_classic_best', group: 'weeklyGroup', label: 'weeklyClassicBest' },
] as const satisfies readonly { field: TournamentUserRankField; group: string; label: string }[];

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

function selectSort(field: TournamentUserRankField) {
    if (field === sortBy.value) return;
    sortBy.value = field;
    currentPage.value = 1;
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

.rank-header-button {
    width: 100%;
    justify-content: flex-end;
    font: inherit;
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
