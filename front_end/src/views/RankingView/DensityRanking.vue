<template>
    <section class="density-ranking">
        <div class="toolbar">
            <div class="board-buttons" :aria-label="t('local.board')">
                <ElButton
                    v-for="option in boardOptions"
                    :key="option.value"
                    size="small"
                    :type="selectedLevel.value === option.value ? 'primary' : 'default'"
                    :plain="selectedLevel.value !== option.value"
                    @click="selectLevel(option)"
                >
                    {{ t('common.level.c', { row: option.row, column: option.column, mine: option.mine }) }}
                </ElButton>
            </div>
        </div>

        <ElTable
            v-loading="loading"
            :data="players"
            border
            table-layout="auto"
            class="ranking-table"
            :empty-text="t('local.empty')"
        >
            <ElTableColumn prop="rank" width="90" align="center" />
            <ElTableColumn :label="t('common.prop.realName')" min-width="180">
                <template #default="{ row }">
                    <PlayerName :user-id="row.player_id" />
                </template>
            </ElTableColumn>
            <ElTableColumn prop="pluck" :label="t('common.prop.pluck')" min-width="130" align="right">
                <template #default="{ row }">
                    <PreviewNumber :id="row.video_id" :text="formatPluck(row.pluck)" />
                </template>
            </ElTableColumn>
            <ElTableColumn prop="mode" :label="t('common.prop.mode')" min-width="100" align="center">
                <template #default="{ row }">
                    {{ t(`common.mode.code${row.mode}`) }}
                </template>
            </ElTableColumn>
            <ElTableColumn prop="timems" :label="t('common.prop.time')" min-width="110" align="right">
                <template #default="{ row }">
                    {{ ms_to_s(row.timems) }}
                </template>
            </ElTableColumn>
            <ElTableColumn prop="bv" label="3BV" min-width="90" align="right" />
            <ElTableColumn prop="upload_time" :label="t('common.prop.upload_time')" min-width="180" align="center">
                <template #default="{ row }">
                    {{ formatDateTime(row.upload_time) }}
                </template>
            </ElTableColumn>
        </ElTable>

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
import { ElButton, ElPagination, ElTable, ElTableColumn, vLoading } from 'element-plus';
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import { httpErrorNotification } from '@/components/Notifications';
import PlayerName from '@/components/PlayerName.vue';
import PreviewNumber from '@/components/PreviewNumber.vue';
import $axios from '@/http';
import { ms_to_s } from '@/utils';
import { CustomLevel, DensityCustomLevelConfigs } from '@/utils/customlevel';
import { toISODateTimeString } from '@/utils/datetime';

interface RankPlayer {
    rank: number;
    player_id: number;
    player_name: string;
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
        nf: '盲扫',
        rank: '排名',
        std: '标准',
    } },
    en: { local: {
        board: 'Board',
        empty: 'No ranking data',
        nf: 'No Flag',
        rank: 'Rank',
        std: 'Standard',
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
                level: selectedLevel.value.value,
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
    if (selectedLevel.value.value === level.value) return;
    selectedLevel.value = level;
    currentPage.value = 1;
    void fetchRanking();
}

function handlePageSizeChange() {
    currentPage.value = 1;
    void fetchRanking();
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

    .board-buttons :deep(.el-button) {
        margin-left: 0;
    }
}
</style>
