<template>
    <div style="display: flex; gap: 1rem">
        <BaseButton class="square-button" :loading="loading" :aria-label="t('local.refresh')" :title="t('local.refresh')" @click="load">
            <BaseIconRefresh />
        </BaseButton>
        <ElCheckbox v-model="nf" class="nf-toggle">
            NF
        </ElCheckbox>
    </div>
    <ElAlert v-if="failed" :title="t('local.failed')" type="error" :closable="false" />
    <ElTable v-loading="loading" :data="rows" row-key="player_id" border class="saolei-ranking-table" :empty-text="t('local.empty')">
        <ElTableColumn type="index" :index="(index) => first + index + 1" />
        <!-- @vue-generic {SaoleiRecord} -->
        <ElTableColumn column-key="player" :label="t('common.prop.player')">
            <template #default="{ row }">
                <PlayerName :user-id="row.player_id" />
            </template>
        </ElTableColumn>
        <ElTableColumn v-for="level in SaoleiLevels" :key="level" :column-key="level" :label="t(`common.level.${level}`)" align="center">
            <SaoleiRankingColumn :level="level" stat="t" :selected="stat" @select="selectStat" />
            <SaoleiRankingColumn :level="level" stat="b" :selected="stat" @select="selectStat" />
        </ElTableColumn>
        <ElTableColumn column-key="sum" :label="t('common.level.sum')" align="center">
            <SaoleiRankingColumn level="sum" stat="t" :selected="stat" @select="selectStat" />
            <SaoleiRankingColumn level="sum" stat="b" :selected="stat" @select="selectStat" />
        </ElTableColumn>
    </ElTable>
    <div class="pagination">
        <ElPagination
            v-model:current-page="currentPage" v-model:page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper" :page-sizes="[20, 50, 100]" :total="total"
        />
    </div>
</template>

<script setup lang="ts">
import '@/styles/button.css';

import { ElAlert, ElCheckbox, ElPagination, ElTable, ElTableColumn, vLoading } from 'element-plus';
import { computed, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import SaoleiRankingColumn from './SaoleiRankingColumn.vue';

import BaseButton from '@/components/common/BaseButton.vue';
import { BaseIconRefresh } from '@/components/common/icon';
import PlayerName from '@/components/PlayerName.vue';
import { fetchSaoleiRanking, SaoleiLevels } from '@/services/saoleiRankingService';
import type { SaoleiField, SaoleiRecord } from '@/services/saoleiRankingService';

const nf = ref(false);
const stat = ref<SaoleiField>('sumt');
const currentPage = ref(1);
const pageSize = ref(20);
const first = computed(() => (currentPage.value - 1) * pageSize.value);
const total = ref(0);
const rows = ref<SaoleiRecord[]>([]);
const loading = ref(false);
const failed = ref(false);
let requestId = 0;

async function load() {
    const current = ++requestId;
    loading.value = true;
    failed.value = false;
    try {
        const data = await fetchSaoleiRanking(nf.value ? 'saolei_nf' : 'saolei', stat.value, first.value, first.value + pageSize.value);
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

function selectStat(selected: SaoleiField) {
    if (selected === stat.value) return;
    stat.value = selected;
}

watch([nf, stat, pageSize], () => {
    currentPage.value = 1;
}, { flush: 'sync' });
watch([nf, stat, pageSize, currentPage], () => {
    rows.value = [];
    void load();
}, { immediate: true });

const i18nMessages = {
    'zh-cn': { local: {
        empty: '暂无纪录',
        failed: '排行榜加载失败',
        refresh: '刷新',
    } },
    en: { local: {
        empty: 'No records',
        failed: 'Unable to load ranking',
        refresh: 'Refresh',
    } },
};
const { t } = useI18n({ messages: i18nMessages });
</script>

<style scoped>
.nf-toggle {
    margin-bottom: 1rem;
}

.pagination {
    margin-top: 1rem;
    overflow-x: auto;
}
</style>
