<template>
    <section class="top-ranking">
        <div class="top-toolbar">
            <label class="checkbox nf-toggle"><input v-model="nf" class="checkbox-input" type="checkbox"> {{ t('common.nf') }}</label>
            <BaseButton class="square-button" :aria-label="t('common.action.refresh')" :title="t('common.action.refresh')" @click="load">
                <BaseIconRefresh :loading="loading" aria-hidden="true" />
            </BaseButton>
        </div>
        <p v-if="failed" role="alert" class="text-danger">
            {{ t('ranking.loadFailed') }}
        </p>
        <BaseTable v-loading="loading" class="top-ranking-table" :empty="rows.length === 0" :column-count="16" :empty-text="t('ranking.empty')" :table-style="{ width: 'auto', marginInline: 'auto' }">
            <template #head>
                <tr>
                    <th rowspan="2" scope="col" class="table-col-rank">
                        #
                    </th>
                    <th rowspan="2" scope="col" class="table-col-player">
                        {{ t('common.prop.player') }}
                    </th>
                    <th v-for="option in topLevels" :key="option" colspan="3" scope="colgroup" class="table-col-center">
                        {{ t(`common.level.${option}`) }}
                    </th>
                    <th colspan="5" scope="colgroup" class="table-col-center top-detail-start" data-cy="top-detail-heading">
                        {{ t('local.details', { level: t(`common.level.${detailAxis.level}`), stat: t(`common.prop.${topStatNames[detailAxis.stat]}`) }) }}
                    </th>
                </tr>
                <tr>
                    <th v-for="axis in topAxes" :key="`${axis.level}${axis.stat}`" scope="col" class="table-col-number" :aria-sort="level === axis.level && stat === axis.stat ? axis.stat === 't' ? 'ascending' : 'descending' : 'none'">
                        <div class="top-stat-controls">
                            <BaseTextButton class="top-stat-header" size="small" :type="level === axis.level && stat === axis.stat ? 'primary' : 'default'" :data-field="`${axis.level}${axis.stat}`" :aria-label="`${t(`common.level.${axis.level}`)} ${t(`common.prop.${topStatNames[axis.stat]}`)}`" :aria-pressed="level === axis.level && stat === axis.stat" @click="selectRanking(axis.level, axis.stat)">
                                {{ t(`common.prop.${topStatNames[axis.stat]}`) }}
                            </BaseTextButton>
                            <BaseTextButton class="top-detail-toggle" size="small" :type="detailAxis.level === axis.level && detailAxis.stat === axis.stat ? 'primary' : 'default'" :data-detail-field="`${axis.level}${axis.stat}`" :aria-pressed="detailAxis.level === axis.level && detailAxis.stat === axis.stat" :aria-label="t('local.showDetails', { level: t(`common.level.${axis.level}`), stat: t(`common.prop.${topStatNames[axis.stat]}`) })" :title="t('local.showDetails', { level: t(`common.level.${axis.level}`), stat: t(`common.prop.${topStatNames[axis.stat]}`) })" @click="selectDetails(axis.level, axis.stat)">
                                <i class="pi pi-eye" aria-hidden="true" />
                            </BaseTextButton>
                        </div>
                    </th>
                    <th v-for="position in 5" :key="position" scope="col" class="table-col-number" :class="{ 'top-detail-start': position === 1 }">
                        {{ position }}
                    </th>
                </tr>
            </template>
            <tr v-for="(row, index) in tableRows" :key="row.player_id">
                <td class="table-col-rank">
                    {{ first + index + 1 }}
                </td>
                <td class="table-col-player">
                    <PlayerName :user-id="row.player_id" />
                </td>
                <td v-for="axis in topAxes" :key="`${axis.level}${axis.stat}`" class="table-col-number" :data-field="`${axis.level}${axis.stat}`" :data-selected="level === axis.level && stat === axis.stat">
                    {{ formatTopValue(topMean(row.records[topField(nf, axis.level, axis.stat)], axis.stat), axis.level, axis.stat) }}
                </td>
                <td v-for="(video, position) in row.videos" :key="position" class="table-col-number top-detail-cell" :class="{ 'top-detail-start': position === 0 }">
                    <VideoPreviewLink v-if="video" :id="video.video_id">
                        {{ formatTopValue(video.value, detailAxis.level, detailAxis.stat) }}
                    </VideoPreviewLink>
                    <span v-else class="text-secondary">{{ formatTopValue(missingTopValue(detailAxis.stat), detailAxis.level, detailAxis.stat) }}</span>
                </td>
            </tr>
        </BaseTable>
        <div class="top-pagination">
            <ElPagination v-model:current-page="page" v-model:page-size="pageSize" layout="total, sizes, prev, pager, next, jumper" :page-sizes="[20, 50, 100]" :total="total" />
        </div>
    </section>
</template>

<script setup lang="ts">
import '@/styles/checkbox.css';
import '@/styles/text.css';
import { ElPagination, vLoading } from 'element-plus';
import { computed, onScopeDispose, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import BaseButton from '@/components/common/BaseButton.vue';
import BaseTable from '@/components/common/BaseTable.vue';
import BaseTextButton from '@/components/common/BaseTextButton.vue';
import { BaseIconRefresh } from '@/components/common/icon';
import PlayerName from '@/components/PlayerName.vue';
import VideoPreviewLink from '@/components/VideoPreviewLink.vue';
import { fetchTopRanking, formatTopValue, missingTopValue, topAxes, topField, topLevels, topMean, topStatNames } from '@/services/topRankingService';
import type { TopRankingPlayer, TopStat } from '@/services/topRankingService';
import type { MS_Level } from '@/utils/ms_const';

const level = ref<MS_Level>('e');
const stat = ref<TopStat>('t');
const detailAxis = ref<{ level: MS_Level; stat: TopStat }>({ level: 'e', stat: 't' });
const nf = ref(false);
const page = ref(1);
const pageSize = ref(20);
const first = computed(() => (page.value - 1) * pageSize.value);
const total = ref(0);
const rows = ref<TopRankingPlayer[]>([]);
const tableRows = computed(() => rows.value.map((row) => ({
    ...row,
    videos: Array.from({ length: 5 }, (_, position) => row.records[topField(nf.value, detailAxis.value.level, detailAxis.value.stat)]?.videos[position]),
})));
const loading = ref(false);
const failed = ref(false);
let controller: AbortController | null = null;
let requestId = 0;

function selectRanking(selectedLevel: MS_Level, selectedStat: TopStat) {
    level.value = selectedLevel;
    stat.value = selectedStat;
    selectDetails(selectedLevel, selectedStat);
}

function selectDetails(selectedLevel: MS_Level, selectedStat: TopStat) {
    detailAxis.value = { level: selectedLevel, stat: selectedStat };
}

async function load() {
    controller?.abort();
    controller = new AbortController();
    const { signal } = controller;
    const request = ++requestId;
    loading.value = true;
    failed.value = false;
    try {
        const data = await fetchTopRanking(level.value, stat.value, nf.value, first.value, first.value + pageSize.value, signal);
        if (request !== requestId) return;
        rows.value = data.players;
        total.value = data.count;
        if (first.value > 0 && first.value >= total.value) page.value = Math.max(1, Math.ceil(total.value / pageSize.value));
    } catch {
        if (request !== requestId || signal.aborted) return;
        failed.value = true;
        rows.value = [];
        total.value = 0;
    } finally {
        if (request === requestId) loading.value = false;
    }
}

watch([level, stat, nf, pageSize], () => {
    page.value = 1;
}, { flush: 'sync' });
watch([level, stat, nf, pageSize, page], () => {
    rows.value = [];
    void load();
}, { immediate: true });
onScopeDispose(() => {
    requestId++; controller?.abort();
});

const i18nMessages = {
    'zh-cn': { local: {
        details: '{level} {stat} 五条成绩',
        showDetails: '查看 {level} {stat} 的五条成绩',
    } },
    en: { local: {
        details: '{level} {stat} Top 5',
        showDetails: 'Show {level} {stat} top five records',
    } },
};
const { t } = useI18n({ messages: i18nMessages });
</script>

<style scoped>
.top-ranking {
    min-width: 0;
}
.top-toolbar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}
.top-stat-controls {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 4px;
}
.top-stat-header {
    justify-content: flex-end;
    width: 100%;
    padding: 0;
}
.top-detail-toggle {
    flex-shrink: 0;
    padding: 2px;
}
.top-detail-toggle[aria-pressed="true"] {
    color: var(--el-color-primary);
}
.top-ranking-table .top-detail-start {
    border-left: 3px double var(--el-border-color-darker);
}
.top-ranking-table td[data-selected="true"] {
    font-weight: 600;
}
.top-pagination {
    margin-top: 8px;
    overflow-x: auto;
}
.top-pagination > :deep(.el-pagination) {
    width: max-content;
    margin-inline: auto;
}
</style>
