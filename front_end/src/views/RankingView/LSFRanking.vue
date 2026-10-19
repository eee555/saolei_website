<template>
    <section class="lsf-ranking">
        <p v-if="failed" role="alert" class="text-danger">
            {{ t('ranking.loadFailed') }}
        </p>
        <BaseTable v-loading="loading" class="lsf-ranking-table" :empty="rows.length === 0" :column-count="12" :empty-text="t('ranking.empty')">
            <template #head>
                <tr>
                    <th scope="col" class="table-col-rank">
                        #
                    </th>
                    <th scope="col" class="table-col-player">
                        {{ t('common.prop.player') }}
                    </th>
                    <template v-for="field in softFields" :key="field">
                        <th scope="col" class="table-col-number" :aria-sort="selected === field ? 'descending' : 'none'">
                            <BaseTextButton :type="selected === field ? 'primary' : 'default'" :data-field="field" :aria-pressed="selected === field" @click="selected = field">
                                {{ columnLabel(field) }}
                            </BaseTextButton>
                        </th>
                        <th v-if="field === 'lsf'" scope="col" class="table-col-number">
                            {{ t('ranking.grade.title') }}
                        </th>
                    </template>
                </tr>
            </template>
            <tr v-for="(row, index) in rows" :key="row.player_id">
                <td class="table-col-rank">
                    {{ start + index + 1 }}
                </td>
                <td class="table-col-player">
                    <PlayerName :user-id="row.player_id" />
                </td>
                <template v-for="field in softFields" :key="field">
                    <td class="table-col-number" :data-field="field" :title="field === 'lsf' ? undefined : formatGradeTitle(row.values[field], field)" :class="{ 'lsf-selected': selected === field }" :style="field === 'lsf' ? undefined : gradeStyle(row.values[field], field)">
                        {{ field === 'lsf' ? row.values[field].toFixed(2) : formatGrade(row.values[field], field) }}
                    </td>
                    <td v-if="field === 'lsf'" class="table-col-number" data-field="lsf-grade" :title="formatGradeTitle(row.values.lsf, 'lsf')" :class="{ 'lsf-selected': selected === 'lsf' }" :style="gradeStyle(row.values.lsf, 'lsf')">
                        {{ formatGrade(row.values.lsf, 'lsf') }}
                    </td>
                </template>
            </tr>
        </BaseTable>
        <div class="lsf-pagination">
            <ElPagination v-model:current-page="page" v-model:page-size="pageSize" layout="total, sizes, prev, pager, next, jumper" :page-sizes="[20, 50, 100]" :total="total" />
        </div>
    </section>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import { ElPagination, vLoading } from 'element-plus';
import { computed, onScopeDispose, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import BaseTable from '@/components/common/BaseTable.vue';
import BaseTextButton from '@/components/common/BaseTextButton.vue';
import PlayerName from '@/components/PlayerName.vue';
import { fetchSoftRanking, softFields, topEquivalentEt, topGrade, topSoftValues } from '@/services/topRankingService';
import type { SoftField, TopRankingPlayer } from '@/services/topRankingService';
import { store } from '@/store';
import { colorThemes } from '@/store/color';

const props = defineProps({ colored: { type: Boolean, default: false } });

const selected = ref<SoftField>('lsf');
const page = ref(1);
const pageSize = ref(20);
const start = computed(() => (page.value - 1) * pageSize.value);
const players = ref<TopRankingPlayer[]>([]);
const rows = computed(() => players.value.map((player) => ({ ...player, values: topSoftValues(player.records, store.topAnchors ?? {}) })));
const total = ref(0);
const loading = ref(false);
const failed = ref(false);
let controller: AbortController | undefined;
let requestId = 0;

function columnLabel(field: SoftField) {
    if (field === 'lsf') return 'LSF';
    const [mode, level] = field.split(':');
    return `${mode === 'nf' ? 'NF ' : ''}${t(`common.level.${level}`)}`;
}

function equivalentEt(value: number, field: SoftField) {
    const baseline = field === 'lsf' || field.endsWith(':sum') ? 4000 : 100;
    return topEquivalentEt(value, store.topAnchors ?? {}, baseline, field.startsWith('nf:'));
}

function gradeStyle(value: number, field: SoftField) {
    if (!props.colored) return undefined;
    const seconds = equivalentEt(value, field);
    return seconds === null ? undefined : colorThemes.grade.value.getStyle(seconds);
}

function formatGradeTitle(value: number, field: SoftField) {
    const seconds = equivalentEt(value, field);
    return seconds === null ? '--' : `${formatGrade(value, field, true)} (${seconds.toFixed(3)} s)`;
}

function formatGrade(value: number, field: SoftField, full = false) {
    const baseline = field === 'lsf' || field.endsWith(':sum') ? 4000 : 100;
    const grade = topGrade(value, store.topAnchors ?? {}, baseline, field.startsWith('nf:'));
    if (grade === null) return '--';
    const fullName = `ranking.grade.fullNames.${grade.index}`;
    const name = full && i18n.te(fullName) ? t(fullName) : t(`ranking.grade.names.${grade.index}`);
    return t('ranking.grade.format', { name, stage: (grade.position * 10).toFixed(1) });
}

async function load() {
    controller?.abort();
    controller = new AbortController();
    const { signal } = controller;
    const request = ++requestId;
    loading.value = true;
    failed.value = false;
    try {
        const result = await fetchSoftRanking(selected.value, start.value, start.value + pageSize.value, signal);
        if (request !== requestId) return;
        players.value = result.players;
        total.value = result.count;
        if (start.value > 0 && start.value >= total.value) page.value = Math.max(1, Math.ceil(total.value / pageSize.value));
    } catch {
        if (signal.aborted || request !== requestId) return;
        failed.value = true;
        players.value = [];
        total.value = 0;
    } finally {
        if (request === requestId) loading.value = false;
    }
}

watch([selected, pageSize], () => {
    page.value = 1;
}, { flush: 'sync' });
watch([selected, pageSize, page], () => {
    void load();
}, { immediate: true });
onScopeDispose(() => {
    requestId++; controller?.abort();
});

defineExpose({ refresh: load, loading });

const i18n = useI18n();
const { t } = i18n;
</script>

<style scoped>
.lsf-ranking {
    min-width: 0;
}
.lsf-selected {
    font-weight: 600;
}
.lsf-pagination {
    margin-top: 8px;
    overflow-x: auto;
}
.lsf-pagination > :deep(.el-pagination) {
    width: max-content;
    margin-inline: auto;
}
</style>
