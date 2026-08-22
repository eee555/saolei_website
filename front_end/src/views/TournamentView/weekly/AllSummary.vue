<template>
    <!-- @vue-generic {WeeklyParticipant} -->
    <ElTable :data="data" :default-sort="{ prop: 'classic_score', order: 'ascending' }" @row-click="handleRowClick">
        <ElTableColumn :label="t('common.prop.realName')" sortable>
            <template #default="{row}">
                <PlayerName v-if="row.user_id !== null" :user-id="row.user_id" />
                <span v-else>{{ t('common.anonymous') }}</span>
            </template>
        </ElTableColumn>
        <ElTableColumn :label="t('common.level.e')">
            <ElTableColumn v-for="index in 2" :key="`e-${index}`" :label="`#${index}`" sortable :sort-method="scoreSort(`classic_et`, index - 1)">
                <template #default="{row}">
                    {{ ms_to_s(row.classic_et[index - 1][1]) }}
                </template>
            </ElTableColumn>
            <ElTableColumn prop="classic_e_sum" :label="t('common.score.sum')" sortable>
                <template #default="{row}">
                    {{ ms_to_s(row.classic_e_sum) }}
                </template>
            </ElTableColumn>
        </ElTableColumn>
        <ElTableColumn :label="t('common.level.i')">
            <ElTableColumn v-for="index in 5" :key="`i-${index}`" :label="`#${index}`" sortable :sort-method="scoreSort(`classic_it`, index - 1)">
                <template #default="{row}">
                    {{ ms_to_s(row.classic_it[index - 1][1]) }}
                </template>
            </ElTableColumn>
            <ElTableColumn prop="classic_i_sum" :label="t('common.score.sum')" sortable>
                <template #default="{row}">
                    {{ ms_to_s(row.classic_i_sum) }}
                </template>
            </ElTableColumn>
        </ElTableColumn>
        <ElTableColumn prop="classic_score" :label="t('common.level.sum')" sortable>
            <template #default="{row}">
                {{ ms_to_s(row.classic_score) }}
            </template>
        </ElTableColumn>
    </ElTable>
</template>

<script setup lang="ts">
import { ElTable, ElTableColumn } from 'element-plus';
import { useI18n } from 'vue-i18n';

import PlayerName from '@/components/PlayerName.vue';
import { ms_to_s } from '@/utils';
import type { WeeklyParticipant } from '@/utils/weekly';

defineProps({
    data: {
        type: Array<WeeklyParticipant>,
        default: () => [],
    },
});

const emit = defineEmits<{
    (event: 'row-click', row: WeeklyParticipant): void;
}>();

const { t } = useI18n();

function scoreSort(field: 'classic_et' | 'classic_it', index: number) {
    return (left: WeeklyParticipant, right: WeeklyParticipant) => left[field][index][1] - right[field][index][1];
}

function handleRowClick(row: WeeklyParticipant) {
    emit('row-click', row);
}
</script>
