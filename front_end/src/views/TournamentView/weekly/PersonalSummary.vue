<template>
    <ElTable :data="summaryRows" :show-header="false">
        <ElTableColumn>
            <template #default="{row}">
                <span class="summary-label">{{ row.intermediate.label }}</span>
                {{ ms_to_s(row.intermediate.timems) }}
            </template>
        </ElTableColumn>
        <ElTableColumn>
            <template #default="{row}">
                <span class="summary-label">{{ row.expert.label }}</span>
                {{ ms_to_s(row.expert.timems) }}
            </template>
        </ElTableColumn>
    </ElTable>
</template>

<script setup lang="ts">
import { ElTable, ElTableColumn } from 'element-plus';
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

import { ms_to_s } from '@/utils';
import type { VideoAbstract } from '@/utils/videoabstract';

const props = defineProps({
    videos: {
        type: Array<VideoAbstract>,
        default: () => [],
    },
});

const { t } = useI18n();

interface WeeklySummaryCell {
    label: string;
    timems: number;
}

interface WeeklySummaryRow {
    intermediate: WeeklySummaryCell;
    expert: WeeklySummaryCell;
}

function bestTimes(level: 'i' | 'e', count: number, defaultTime: number) {
    const times = props.videos.
        filter((video) => video.level === level && video.timems < defaultTime).
        map((video) => video.timems).
        sort((left, right) => left - right).
        slice(0, count);
    while (times.length < count) {
        times.push(defaultTime);
    }
    return times;
}

const summaryRows = computed<WeeklySummaryRow[]>(() => {
    const intermediateTimes = bestTimes('i', 5, 60000);
    const expertTimes = bestTimes('e', 2, 240000);
    const intermediateSum = intermediateTimes.reduce((sum, timems) => sum + timems, 0);
    const expertSum = expertTimes.reduce((sum, timems) => sum + timems, 0);
    const expertCells: WeeklySummaryCell[] = [
        { label: `${t('common.level.e')} #1`, timems: expertTimes[0] },
        { label: `${t('common.level.e')} #2`, timems: expertTimes[1] },
        { label: `${t('common.level.i')} ${t('common.score.sum')}`, timems: intermediateSum },
        { label: `${t('common.level.e')} ${t('common.score.sum')}`, timems: expertSum },
        { label: t('common.level.sum'), timems: intermediateSum + expertSum },
    ];
    return intermediateTimes.map((timems, index) => ({
        intermediate: {
            label: `${t('common.level.i')} #${index + 1}`,
            timems,
        },
        expert: expertCells[index],
    }));
});
</script>

<style scoped>
.summary-label {
    display: inline-block;
    min-width: 8em;
    color: var(--el-text-color-secondary);
}
</style>
