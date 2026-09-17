<template>
    <ElTable :data="data" :default-sort="{ prop: 'classic_score', order: 'ascending' }" @row-click="handleRowClick">
        <!-- @vue-generic {WeeklyParticipant} -->
        <ElTableColumn :label="t('common.prop.realName')" sortable>
            <template #default="{row}">
                <PlayerName v-if="row.user_id !== 0" :user-id="row.user_id" />
                <span v-else>{{ t('common.anonymous') }}</span>
            </template>
        </ElTableColumn>
        <ElTableColumn :label="t('common.level.e')">
            <!-- @vue-generic {WeeklyParticipant} -->
            <ElTableColumn v-for="index in 2" :key="`e-${index}`" :label="`#${index}`" sortable :sort-method="scoreSort(`classic_et`, index - 1)">
                <template #default="{row}">
                    <ElLink @click.stop="preview(row.classic_et[index - 1][0])">
                        {{ ms_to_s(row.classic_et[index - 1][1]) }}
                    </ElLink>
                </template>
            </ElTableColumn>
            <!-- @vue-generic {WeeklyParticipant} -->
            <ElTableColumn prop="classic_e_sum" :label="t('common.score.sum')" sortable>
                <template #default="{row}">
                    {{ ms_to_s(row.classic_e_sum) }}
                </template>
            </ElTableColumn>
        </ElTableColumn>
        <ElTableColumn :label="t('common.level.i')">
            <!-- @vue-generic {WeeklyParticipant} -->
            <ElTableColumn v-for="index in 5" :key="`i-${index}`" :label="`#${index}`" sortable :sort-method="scoreSort(`classic_it`, index - 1)">
                <template #default="{row}">
                    <ElLink @click="preview(row.classic_it[index - 1][0])">
                        {{ ms_to_s(row.classic_it[index - 1][1]) }}
                    </ElLink>
                </template>
            </ElTableColumn>
            <!-- @vue-generic {WeeklyParticipant} -->
            <ElTableColumn prop="classic_i_sum" :label="t('common.score.sum')" sortable>
                <template #default="{row}">
                    {{ ms_to_s(row.classic_i_sum) }}
                </template>
            </ElTableColumn>
        </ElTableColumn>
        <!-- @vue-generic {WeeklyParticipant} -->
        <ElTableColumn prop="classic_score" :label="t('common.level.sum')" sortable>
            <template #default="{row}">
                {{ ms_to_s(row.classic_score) }}
            </template>
        </ElTableColumn>
    </ElTable>
</template>

<script setup lang="ts">
import { ElLink, ElTable, ElTableColumn } from 'element-plus';
import { useI18n } from 'vue-i18n';

import PlayerName from '@/components/PlayerName.vue';
import { ms_to_s } from '@/utils';
import { preview } from '@/utils/common/PlayerDialog';
import type { WeeklyParticipant } from '@/utils/weekly';

defineProps({
    data: { type: Array<WeeklyParticipant>, default: () => [] },
});

const emit = defineEmits<{
    'row-click': [row: WeeklyParticipant];
}>();

const { t } = useI18n();

function scoreSort(field: 'classic_et' | 'classic_it', index: number) {
    return (left: WeeklyParticipant, right: WeeklyParticipant) => left[field][index][1] - right[field][index][1];
}

function handleRowClick(row: WeeklyParticipant) {
    emit('row-click', row);
}
</script>
