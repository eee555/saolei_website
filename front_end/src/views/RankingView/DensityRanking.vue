<template>
    <section class="density-ranking">
        <div class="toolbar">
            <div class="board-buttons" :aria-label="t('local.board')">
                <BaseButton
                    v-for="option in boardOptions"
                    :key="option.code"
                    size="small"
                    :type="selectedLevel.code === option.code ? 'primary' : 'default'"
                    :plain="selectedLevel.code !== option.code"
                    :aria-pressed="selectedLevel.code === option.code"
                    @click="selectLevel(option)"
                >
                    {{ t('common.level.c', { row: option.row, column: option.column, mine: option.mine }) }}
                </BaseButton>
            </div>
        </div>

        <BaseTable v-loading="loading" class="ranking-table" :table-style="{ width: 'auto', marginInline: 'auto' }" :empty="players.length === 0" :empty-text="t('local.empty')" :column-count="7">
            <template #head>
                <tr>
                    <th scope="col" class="table-col-rank">
                        {{ t('local.rank') }}
                    </th>
                    <th scope="col" class="table-col-player">
                        {{ t('common.prop.realName') }}
                    </th>
                    <th scope="col" class="table-col-number">
                        {{ t('common.prop.pluck') }}
                    </th>
                    <th scope="col" class="table-col-mode">
                        {{ t('common.prop.mode') }}
                    </th>
                    <th scope="col" class="table-col-number">
                        {{ t('common.prop.time') }}
                    </th>
                    <th scope="col" class="table-col-bv">
                        {{ t('common.prop.bv') }}
                    </th>
                    <th scope="col" class="table-col-datetime">
                        {{ t('common.prop.upload_time') }}
                    </th>
                </tr>
            </template>
            <tr v-for="(row, index) in players" :key="row.player_id">
                <td class="table-col-rank">
                    {{ getRank(index) }}
                </td>
                <td class="table-col-player">
                    <PlayerName :user-id="row.player_id" />
                </td>
                <td class="table-col-number">
                    <PreviewNumber :id="row.video_id" :text="formatPluck(row.pluck)" />
                </td>
                <td class="table-col-mode">
                    {{ t(`common.mode.code${row.mode}`) }}
                </td>
                <td class="table-col-number">
                    {{ ms_to_s(row.timems) }}
                </td>
                <td class="table-col-bv">
                    {{ row.bv }}
                </td>
                <td class="table-col-datetime">
                    {{ formatDateTime(row.upload_time) }}
                </td>
            </tr>
        </BaseTable>

        <ElPagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            class="pagination"
            layout="total, sizes, prev, pager, next, jumper"
            :page-sizes="[20, 50, 100]"
            :total="totalCount"
            @size-change="handlePageSizeChange"
            @current-change="fetchRanking"
        />
    </section>
</template>

<script setup lang="ts">
import { ElPagination, vLoading } from 'element-plus';
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import BaseButton from '@/components/common/BaseButton.vue';
import BaseTable from '@/components/common/BaseTable.vue';
import { httpErrorNotification } from '@/components/Notifications';
import PlayerName from '@/components/PlayerName.vue';
import PreviewNumber from '@/components/PreviewNumber.vue';
import $axios from '@/http';
import { ms_to_s } from '@/utils';
import { CustomLevel, DensityCustomLevelConfigs } from '@/utils/customlevel';
import { toISODateTimeString } from '@/utils/datetime';

interface RankPlayer {
    player_id: number;
    video_id: number;
    mode: string;
    pluck: number;
    timems: number;
    bv: number;
    upload_time: string;
}

interface RankResponse {
    count: number;
    players: RankPlayer[];
}

const i18nMessages = {
    'zh-cn': { local: {
        board: '局面',
        empty: '暂无排行数据',
        rank: '排名',
    } },
    en: { local: {
        board: 'Board',
        empty: 'No ranking data',
        rank: 'Rank',
    } },
};

const { t } = useI18n({ messages: i18nMessages });

const boardOptions = ref<CustomLevel[]>([...DensityCustomLevelConfigs]);

const selectedLevel = ref(new CustomLevel(8, 8, 40));
const currentPage = ref(1);
const pageSize = ref(20);
const totalCount = ref(0);
const players = ref<RankPlayer[]>([]);
const loading = ref(false);

async function fetchRanking() {
    loading.value = true;
    const start = (currentPage.value - 1) * pageSize.value;
    const end = start + pageSize.value;
    try {
        const { data } = await $axios.get<RankResponse>('/api/customranking/pluck', {
            params: {
                level: selectedLevel.value.code,
                start,
                end,
            },
        });
        players.value = data.players;
        totalCount.value = data.count;
    } catch (error) {
        httpErrorNotification(error);
    } finally {
        loading.value = false;
    }
}

function selectLevel(level: CustomLevel) {
    if (selectedLevel.value.code === level.code) return;
    selectedLevel.value = level;
    currentPage.value = 1;
    void fetchRanking();
}

function handlePageSizeChange() {
    currentPage.value = 1;
    void fetchRanking();
}

function getRank(index: number): number {
    return (currentPage.value - 1) * pageSize.value + index + 1;
}

function formatPluck(value: number): string {
    return value.toFixed(6);
}

function formatDateTime(value: string): string {
    return toISODateTimeString(new Date(value));
}

onMounted(() => {
    void fetchRanking();
});
</script>

<style scoped>
.density-ranking {
    width: min(1120px, calc(100vw - 32px));
    margin: 0 auto;
}

.toolbar {
    margin: 12px 0 16px;
}

.board-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.board-buttons > .base-button {
    margin: 0;
}

.ranking-table {
    width: 100%;
}

.pagination {
    justify-content: center;
    margin-top: 16px;
}

@media (max-width: 640px) {
    .density-ranking {
        width: calc(100vw - 16px);
    }

    .toolbar {
        display: block;
    }

    .board-buttons {
        gap: 6px;
    }
}
</style>
