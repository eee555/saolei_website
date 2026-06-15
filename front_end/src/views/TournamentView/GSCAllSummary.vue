<template>
    <ElTable :data="data" :default-sort="{ prop: 'sum_tsum', order: 'ascending' }" @row-click="handleRowClick">
        <ElTableColumn prop="user__realname" sortable>
            <template #default="{ row }: { row: GSCParticipant }">
                <PlayerName :user-id="row.user__id" />
            </template>
        </ElTableColumn>
        <ElTableColumn :label="t('common.level.b')">
            <ElTableColumn prop="bt1st" :label="t('common.score.best')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.bt1st) }}
                </template>
            </ElTableColumn>
            <ElTableColumn prop="bt20th" :label="t('common.score.edge')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.bt20th) }}
                </template>
            </ElTableColumn>
            <ElTableColumn prop="bt20sum" :label="t('common.score.sum')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.bt20sum) }}
                </template>
            </ElTableColumn>
        </ElTableColumn>
        <ElTableColumn :label="t('common.level.i')">
            <ElTableColumn prop="it1st" :label="t('common.score.best')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.it1st) }}
                </template>
            </ElTableColumn>
            <ElTableColumn prop="it12th" :label="t('common.score.edge')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.it12th) }}
                </template>
            </ElTableColumn>
            <ElTableColumn prop="it12sum" :label="t('common.score.sum')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.it12sum) }}
                </template>
            </ElTableColumn>
        </ElTableColumn>
        <ElTableColumn :label="t('common.level.e')">
            <ElTableColumn prop="et1st" :label="t('common.score.best')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.et1st) }}
                </template>
            </ElTableColumn>
            <ElTableColumn prop="et5th" :label="t('common.score.edge')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.et5th) }}
                </template>
            </ElTableColumn>
            <ElTableColumn prop="et5sum" :label="t('common.score.sum')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.et5sum) }}
                </template>
            </ElTableColumn>
        </ElTableColumn>
        <ElTableColumn :label="t('common.level.sum')">
            <ElTableColumn prop="sum_tbest" :label="t('common.score.best')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.sum_tbest) }}
                </template>
            </ElTableColumn>
            <ElTableColumn prop="sum_tedge" :label="t('common.score.edge')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.sum_tedge) }}
                </template>
            </ElTableColumn>
            <ElTableColumn prop="sum_tsum" :label="t('common.score.sum')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.sum_tsum) }}
                </template>
            </ElTableColumn>
        </ElTableColumn>
    </ElTable>
</template>

<script setup lang="ts">
import { ElTable, ElTableColumn } from 'element-plus';
import { useI18n } from 'vue-i18n';

import PlayerName from '@/components/PlayerName.vue';
import { ms_to_s } from '@/utils';
import { GSCParticipant } from '@/utils/gsc';

defineProps({
    data: {
        type: Array<GSCParticipant>,
        default: () => [],
    },
});

const emit = defineEmits(['row-click']);

const { t } = useI18n();

function handleRowClick(row: GSCParticipant) {
    emit('row-click', row);
}
</script>
