<template>
    <section class="pb-ranking">
        <div class="pb-toolbar">
            <ElCheckbox v-model="nf" class="nf-toggle">
                NF
            </ElCheckbox>
            <PBBVButton v-for="optionLevel in pbLevels" :key="optionLevel" :level="optionLevel" :selected-level="level" :selected-bv="bv" :nf="nf" :counts="counts" @select="selectBucket(optionLevel, $event)" />
            <BaseButton class="square-button" :loading="loading || countsLoading" :aria-label="t('local.refresh')" :title="t('local.refresh')" @click="refresh">
                <BaseIconRefresh />
            </BaseButton>
        </div>
        <ElAlert v-if="failed" :title="t('local.failed')" type="error" :closable="false" />
        <ElAlert v-if="countsFailed" :title="t('local.countsFailed')" type="error" :closable="false" />
        <ElTable v-loading="loading" :data="rows" row-key="player_id" border class="pb-ranking-table" :empty-text="t('local.empty')">
            <ElTableColumn type="index" label="#" :index="(index) => first + index + 1" width="60" align="center" />
            <!-- @vue-generic {PBRankingPlayer} -->
            <ElTableColumn column-key="player" :label="t('common.prop.player')" min-width="150">
                <template #default="{ row }">
                    <PlayerName :user-id="row.player_id" />
                </template>
            </ElTableColumn>
            <!-- @vue-generic {PBRankingPlayer} -->
            <ElTableColumn v-for="stat in pbStats" :key="stat" :column-key="stat" :label="t(`common.prop.${stat}`)" min-width="100" align="right">
                <template #default="{ row }">
                    <PreviewNumber v-if="stat === 'time'" :id="row.video_id" :text="formatPBValue(row.timems, level, bv, stat)" />
                    <span v-else>{{ formatPBValue(row.timems, level, bv, stat) }}</span>
                </template>
            </ElTableColumn>
            <!-- @vue-generic {PBRankingPlayer} -->
            <ElTableColumn prop="upload_time" :label="t('common.prop.upload_time')" min-width="170" align="center">
                <template #default="{ row }">
                    {{ formatPBUploadTime(row.upload_time) }}
                </template>
            </ElTableColumn>
        </ElTable>
        <div class="pb-pagination">
            <ElPagination v-model:current-page="currentPage" v-model:page-size="pageSize" layout="total, sizes, prev, pager, next, jumper" :page-sizes="[20, 50, 100]" :total="total" />
        </div>
    </section>
</template>

<script setup lang="ts">
import { ElAlert, ElCheckbox, ElPagination, ElTable, ElTableColumn, vLoading } from 'element-plus';
import { computed, onMounted, onScopeDispose, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import PBBVButton from './PBBVButton.vue';

import BaseButton from '@/components/common/BaseButton.vue';
import { BaseIconRefresh } from '@/components/common/icon';
import PlayerName from '@/components/PlayerName.vue';
import PreviewNumber from '@/components/PreviewNumber.vue';
import { fetchPBCounts, fetchPBRanking, formatPBUploadTime, formatPBValue, pbLevels, pbStats } from '@/services/pbRankingService';
import type { PBCounts, PBRankingPlayer } from '@/services/pbRankingService';
import type { MS_Level } from '@/utils/ms_const';

const level = ref<MS_Level>('b');
const bv = ref(1);
const nf = ref(false);
const counts = ref<PBCounts>({});
const countsLoading = ref(false);
const countsFailed = ref(false);
const currentPage = ref(1);
const pageSize = ref(20);
const first = computed(() => (currentPage.value - 1) * pageSize.value);
const total = ref(0);
const rows = ref<PBRankingPlayer[]>([]);
const loading = ref(false);
const failed = ref(false);
let requestId = 0;
let countsRequestId = 0;

function selectBucket(selectedLevel: MS_Level, selectedBV: number) {
    level.value = selectedLevel;
    bv.value = selectedBV;
}

async function loadCounts() {
    const current = ++countsRequestId;
    countsLoading.value = true;
    countsFailed.value = false;
    try {
        const data = await fetchPBCounts();
        if (current === countsRequestId) counts.value = data;
    } catch {
        if (current === countsRequestId) countsFailed.value = true;
    } finally {
        if (current === countsRequestId) countsLoading.value = false;
    }
}

function refresh() {
    void loadCounts();
    void load();
}

async function load() {
    const current = ++requestId;
    loading.value = true;
    failed.value = false;
    try {
        const data = await fetchPBRanking(level.value, bv.value, nf.value, first.value, first.value + pageSize.value);
        if (current !== requestId) return;
        rows.value = data.players;
        total.value = data.count;
        if (first.value > 0 && first.value >= total.value) {
            currentPage.value = Math.max(1, Math.ceil(total.value / pageSize.value));
        }
    } catch {
        if (current !== requestId) return;
        rows.value = [];
        total.value = 0;
        failed.value = true;
    } finally {
        if (current === requestId) loading.value = false;
    }
}

watch([level, bv, nf, pageSize], () => {
    currentPage.value = 1;
}, { flush: 'sync' });
watch([level, bv, nf, pageSize, currentPage], () => {
    rows.value = [];
    void load();
}, { immediate: true });
onMounted(() => {
    void loadCounts();
});
onScopeDispose(() => {
    requestId++;
    countsRequestId++;
});

const i18nMessages = {
    'zh-cn': { local: {
        empty: '暂无纪录',
        failed: '排行榜加载失败',
        countsFailed: '各榜人数加载失败',
        refresh: '刷新',
    } },
    en: { local: {
        empty: 'No records',
        failed: 'Unable to load ranking',
        countsFailed: 'Unable to load board counts',
        refresh: 'Refresh',
    } },
};
const { t } = useI18n({ messages: i18nMessages });
</script>

<style scoped>
.pb-ranking {
    min-width: 0;
}

.pb-toolbar {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 8px;
}

.pb-pagination {
    margin-top: 8px;
    overflow-x: auto;
}
</style>
