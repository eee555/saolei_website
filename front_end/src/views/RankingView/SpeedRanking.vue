<template>
    <section class="speed-ranking">
        <div class="ranking-toolbar">
            <h2>Saolei.wang</h2>
            <ElCheckbox v-model="nf" @change="resetPage">
                NF
            </ElCheckbox>
        </div>
        <ElAlert v-if="failed" :title="t('local.failed')" type="error" :closable="false">
            <ElButton :icon="Refresh" :loading="loading" :aria-label="t('local.retry')" :title="t('local.retry')" @click="load" />
        </ElAlert>
        <PrDataTable
            :value="rows" :loading="loading" data-key="player_id" lazy paginator
            :first="first" :rows="pageSize" :total-records="total" :rows-per-page-options="[20, 50, 100]"
            scrollable table-style="min-width: 65rem" @page="onPage"
        >
            <template #empty>
                {{ t('local.empty') }}
            </template>
            <PrColumn column-key="rank" :header="t('local.rank')" style="width: 5rem">
                <template #body="{ index }">
                    {{ first + index + 1 }}
                </template>
            </PrColumn>
            <PrColumn column-key="player" :header="t('local.player')" style="min-width: 10rem">
                <template #body="{ data }">
                    <PlayerName :user-id="data.player_id" />
                </template>
            </PrColumn>
            <PrColumn v-for="column in speedStats" :key="column" :column-key="column" :field="column" style="min-width: 6rem">
                <template #header>
                    <button class="stat-header" type="button" :aria-pressed="stat === column" @click="selectStat(column)">
                        {{ t(`local.${column}`) }}
                        <ElIcon v-if="stat === column" aria-hidden="true">
                            <ArrowUp v-if="isTimeStat(stat)" />
                            <ArrowDown v-else />
                        </ElIcon>
                    </button>
                </template>
                <template #body="{ data }">
                    <PreviewNumber v-if="speedVideoId(data, column)" :id="speedVideoId(data, column)" :text="formatSpeedValue(data, column)" />
                    <span v-else>{{ formatSpeedValue(data, column) }}</span>
                </template>
            </PrColumn>
        </PrDataTable>
    </section>
</template>

<script setup lang="ts">
import { ArrowDown, ArrowUp, Refresh } from '@element-plus/icons-vue';
import { ElAlert, ElButton, ElCheckbox, ElIcon } from 'element-plus';
import PrColumn from 'primevue/column';
import PrDataTable from 'primevue/datatable';
import type { DataTablePageEvent } from 'primevue/datatable';
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import PlayerName from '@/components/PlayerName.vue';
import PreviewNumber from '@/components/PreviewNumber.vue';
import { fetchSpeedRanking, formatSpeedValue, isTimeStat, speedStats, speedVideoId } from '@/services/speedrankingService';
import type { SpeedRecord, SpeedStat } from '@/services/speedrankingService';

const nf = ref(false);
const stat = ref<SpeedStat>('sumt');
const first = ref(0);
const pageSize = ref(20);
const total = ref(0);
const rows = ref<SpeedRecord[]>([]);
const loading = ref(false);
const failed = ref(false);
let requestId = 0;

async function load() {
    const current = ++requestId;
    loading.value = true;
    failed.value = false;
    try {
        const data = await fetchSpeedRanking(nf.value ? 'saolei_nf' : 'saolei', stat.value, first.value, first.value + pageSize.value);
        if (current !== requestId) return;
        rows.value = data.players;
        total.value = data.count;
        if (first.value > 0 && first.value >= total.value) {
            first.value = Math.max(0, Math.ceil(total.value / pageSize.value) - 1) * pageSize.value;
            await load();
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

function resetPage() {
    first.value = 0;
    rows.value = [];
    void load();
}

function onPage(event: DataTablePageEvent) {
    first.value = event.first;
    pageSize.value = event.rows;
    void load();
}

function selectStat(selected: SpeedStat) {
    if (selected === stat.value) return;
    stat.value = selected;
    resetPage();
}

onMounted(load);

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
.speed-ranking { min-width: 0; }
.ranking-toolbar { display: flex; align-items: center; gap: 1.5rem; margin-bottom: 1rem; }
h2 { font-size: 1.1rem; margin: 0; }
.stat-header { display: flex; align-items: center; gap: 0.4rem; border: 0; background: transparent; color: inherit; font: inherit; text-align: left; padding: 0; cursor: pointer; }
.stat-header[aria-pressed="true"] { color: var(--el-color-primary); }
</style>
