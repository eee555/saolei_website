<template>
    <ElCheckbox v-model="nf" class="nf-toggle">
        NF
    </ElCheckbox>
    <ElAlert v-if="failed" :title="t('local.failed')" type="error" :closable="false">
        <ElButton :icon="Refresh" :loading="loading" :aria-label="t('local.retry')" :title="t('local.retry')" @click="load" />
    </ElAlert>
    <ElTable v-loading="loading" :data="rows" row-key="player_id" border class="saolei-ranking-table" :empty-text="t('local.empty')">
        <ElTableColumn column-key="rank" :label="t('local.rank')" width="80">
            <template #default="{ $index }">
                {{ first + $index + 1 }}
            </template>
        </ElTableColumn>
        <!-- @vue-generic {SaoleiRecord} -->
        <ElTableColumn column-key="player" :label="t('local.player')" min-width="160">
            <template #default="{ row }">
                <PlayerName :user-id="row.player_id" />
            </template>
        </ElTableColumn>
        <!-- @vue-generic {SaoleiRecord} -->
        <ElTableColumn v-for="column in saoleiStats" :key="column" :column-key="column" :prop="column" :label="t(`local.${column}`)" min-width="115">
            <template #header>
                <button class="stat-header" type="button" :aria-pressed="stat === column" @click="selectStat(column)">
                    {{ t(`local.${column}`) }}
                    <ElIcon v-if="stat === column" aria-hidden="true">
                        <ArrowUp v-if="isSaoleiTimeStat(stat)" />
                        <ArrowDown v-else />
                    </ElIcon>
                </button>
            </template>
            <template #default="{ row }">
                <PreviewNumber v-if="saoleiVideoId(row, column)" :id="saoleiVideoId(row, column)" :text="formatSaoleiValue(row, column)" />
                <span v-else>{{ formatSaoleiValue(row, column) }}</span>
            </template>
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
import { ArrowDown, ArrowUp, Refresh } from '@element-plus/icons-vue';
import { ElAlert, ElButton, ElCheckbox, ElIcon, ElPagination, ElTable, ElTableColumn, vLoading } from 'element-plus';
import { computed, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import PlayerName from '@/components/PlayerName.vue';
import PreviewNumber from '@/components/PreviewNumber.vue';
import { fetchSaoleiRanking, formatSaoleiValue, isSaoleiTimeStat, saoleiStats, saoleiVideoId } from '@/services/saoleiRankingService';
import type { SaoleiRecord, SaoleiStat } from '@/services/saoleiRankingService';

const nf = ref(false);
const stat = ref<SaoleiStat>('sumt');
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

function selectStat(selected: SaoleiStat) {
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
        rank: '排名',
        player: '玩家',
        empty: '暂无纪录',
        failed: '排行榜加载失败',
        retry: '重试',
        bt: '初级 Time',
        bb: '初级 3BV/s',
        it: '中级 Time',
        ib: '中级 3BV/s',
        et: '高级 Time',
        eb: '高级 3BV/s',
        sumt: '总 Time',
        sumb: '总 3BV/s',
    } },
    en: { local: {
        rank: 'Rank',
        player: 'Player',
        empty: 'No records',
        failed: 'Unable to load ranking',
        retry: 'Retry',
        bt: 'Beg Time',
        bb: 'Beg 3BV/s',
        it: 'Int Time',
        ib: 'Int 3BV/s',
        et: 'Exp Time',
        eb: 'Exp 3BV/s',
        sumt: 'Total Time',
        sumb: 'Total 3BV/s',
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

.stat-header {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    border: 0;
    background: transparent;
    color: inherit;
    font: inherit;
    text-align: left;
    padding: 0;
    cursor: pointer;
}

.stat-header[aria-pressed="true"] {
    color: var(--el-color-primary);
}
</style>
