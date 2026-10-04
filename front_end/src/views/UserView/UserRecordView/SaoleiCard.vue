<template>
    <section v-loading="loading" class="saolei-record-scroll">
        <table class="saolei-record-table">
            <thead>
                <tr>
                    <th scope="col">
                        {{ t('ranking.saolei.title') }}
                    </th>
                    <th v-for="level in levels" :key="level" scope="col">
                        {{ t(`common.level.${level}`) }}
                    </th>
                </tr>
            </thead>
            <tbody>
                <template v-for="rankingName in rankingNames" :key="rankingName">
                    <tr v-for="(label, stat) in SaoleiStat" :key="stat">
                        <th scope="row">
                            {{ t(`common.prop.${label}`) }}{{ rankingName === 'saolei_nf' ? ' (NF)' : '' }}
                        </th>
                        <td v-for="level in levels" :key="level">
                            <PreviewNumber
                                v-if="saoleiVideoId(records[rankingName], `${level}${stat}`)"
                                :id="saoleiVideoId(records[rankingName], `${level}${stat}`)"
                                :text="formatScore(records[rankingName], `${level}${stat}`)"
                            />
                            <span v-else>{{ formatScore(records[rankingName], `${level}${stat}`) }}</span>
                        </td>
                    </tr>
                </template>
            </tbody>
        </table>
    </section>
</template>

<script setup lang="ts">
import { ElMessage, vLoading } from 'element-plus';
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import PreviewNumber from '@/components/PreviewNumber.vue';
import { fetchSaoleiRecords, formatSaoleiValue, SaoleiLevels, SaoleiStat, saoleiVideoId } from '@/services/saoleiRankingService';
import type { SaoleiField, SaoleiPlayerRecord, SaoleiRankingName } from '@/services/saoleiRankingService';

const props = defineProps({
    userId: { type: Number, required: true },
});
const records = ref<Partial<Record<SaoleiRankingName, SaoleiPlayerRecord>>>({});
const loading = ref(false);
const rankingNames: SaoleiRankingName[] = ['saolei', 'saolei_nf'];
const levels = [...SaoleiLevels, 'sum'] as const;
const { t } = useI18n();

watch(() => props.userId, async (userId, _, onCleanup) => {
    let active = true;
    onCleanup(() => {
        active = false;
    });
    records.value = {};
    loading.value = false;
    if (!userId) return;
    loading.value = true;
    try {
        const data = await fetchSaoleiRecords(userId);
        if (active) records.value = data;
    } catch {
        if (active) ElMessage.error({ message: '竞速纪录加载失败', offset: 68 });
    } finally {
        if (active) loading.value = false;
    }
}, { immediate: true });

function formatScore(record: SaoleiPlayerRecord | undefined, stat: SaoleiField): string {
    return `${formatSaoleiValue(record, stat)}(${record?.ranks[stat] ?? '--'})`;
}
</script>

<style scoped>
.saolei-record-scroll {
    overflow-x: auto;
}

.saolei-record-table {
    width: 100%;
    border-collapse: collapse;
    color: var(--el-text-color-regular);
    background: var(--el-fill-color-blank);
    font-size: var(--el-font-size-base);
}

.saolei-record-table th,
.saolei-record-table td {
    border: 1px solid var(--el-border-color-lighter);
    padding: 8px 12px;
    text-align: center;
}

.saolei-record-table th {
    color: var(--el-text-color-secondary);
    background: var(--el-fill-color-light);
}

.saolei-record-table td {
    white-space: nowrap;
}

.saolei-record-table tbody tr:hover {
    background: var(--el-fill-color-lighter);
}
</style>
