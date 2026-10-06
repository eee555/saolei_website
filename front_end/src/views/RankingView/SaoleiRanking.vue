<template>
    <div style="display: flex; gap: 1rem">
        <BaseButton class="square-button" :loading="loading" :aria-label="t('common.action.refresh')" :title="t('common.action.refresh')" @click="load">
            <BaseIconRefresh />
        </BaseButton>
        <ElCheckbox v-model="nf" class="nf-toggle">
            {{ t('common.nf') }}
        </ElCheckbox>
    </div>
    <ElAlert v-if="failed" :title="t('ranking.loadFailed')" type="error" :closable="false" />
    <BaseTable v-loading="loading" class="saolei-ranking-table" :table-style="{ width: 'auto', marginInline: 'auto' }" :empty="rows.length === 0" :column-count="2 + saoleiFields.length" :empty-text="t('ranking.empty')">
        <template #head>
            <tr>
                <th rowspan="2" scope="col" class="table-col-rank" />
                <th rowspan="2" scope="col" class="table-col-player">
                    {{ t('common.prop.player') }}
                </th>
                <th v-for="level in levels" :key="level" colspan="2" scope="colgroup" class="table-col-center">
                    {{ t(`common.level.${level}`) }}
                </th>
            </tr>
            <tr>
                <template v-for="level in levels" :key="level">
                    <th scope="col" class="table-col-number">
                        <SaoleiRankingColumn :level="level" stat="t" :selected="stat" @select="selectStat" />
                    </th>
                    <th scope="col" class="table-col-number">
                        <SaoleiRankingColumn :level="level" stat="b" :selected="stat" @select="selectStat" />
                    </th>
                </template>
            </tr>
        </template>
        <tr v-for="(row, index) in rows" :key="row.player_id">
            <td class="table-col-rank">
                {{ first + index + 1 }}
            </td>
            <td class="table-col-player">
                <PlayerName :user-id="row.player_id" />
            </td>
            <td v-for="field in saoleiFields" :key="field" class="table-col-number">
                <PreviewNumber v-if="saoleiVideoId(row, field)" :id="saoleiVideoId(row, field)" :text="formatSaoleiValue(row, field)" />
                <span v-else>{{ formatSaoleiValue(row, field) }}</span>
            </td>
        </tr>
    </BaseTable>
    <div class="pagination">
        <ElPagination
            v-model:current-page="currentPage" v-model:page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper" :page-sizes="[20, 50, 100]" :total="total"
        />
    </div>
</template>

<script setup lang="ts">
import '@/styles/button.css';

import { ElAlert, ElCheckbox, ElPagination, vLoading } from 'element-plus';
import { computed, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import SaoleiRankingColumn from './SaoleiRankingColumn.vue';

import BaseButton from '@/components/common/BaseButton.vue';
import BaseTable from '@/components/common/BaseTable.vue';
import { BaseIconRefresh } from '@/components/common/icon';
import PlayerName from '@/components/PlayerName.vue';
import PreviewNumber from '@/components/PreviewNumber.vue';
import { fetchSaoleiRanking, formatSaoleiValue, saoleiFields, SaoleiLevels, saoleiVideoId } from '@/services/saoleiRankingService';
import type { SaoleiField, SaoleiRecord } from '@/services/saoleiRankingService';

const levels = [...SaoleiLevels, 'sum'] as const;
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

const { t } = useI18n();
</script>

<style scoped>
.nf-toggle {
    margin-bottom: 1rem;
}

.pagination {
    margin-top: 1rem;
    overflow-x: auto;
}

.pagination > :deep(.el-pagination) {
    width: max-content;
    margin-inline: auto;
}
</style>
