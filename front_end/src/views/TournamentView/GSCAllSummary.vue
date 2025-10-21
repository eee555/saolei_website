<template>
    <el-table :data="data" @row-click="handleRowClick">
        <el-table-column prop="user__realname" sortable>
            <template #default="{ row }: { row: GSCParticipant }">
                <PlayerName :user-id="row.user__id" :user-name="row.user__realname" />
            </template>
        </el-table-column>
        <el-table-column :label="t('common.level.b')">
            <el-table-column prop="bt1st" :label="t('common.score.best')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.bt1st) }}
                </template>
            </el-table-column>
            <el-table-column prop="bt20th" :label="t('common.score.edge')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.bt20th) }}
                </template>
            </el-table-column>
            <el-table-column prop="bt20sum" :label="t('common.score.sum')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.bt20sum) }}
                </template>
            </el-table-column>
        </el-table-column>
        <el-table-column :label="t('common.level.i')">
            <el-table-column prop="it1st" :label="t('common.score.best')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.it1st) }}
                </template>
            </el-table-column>
            <el-table-column prop="it12th" :label="t('common.score.edge')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.it12th) }}
                </template>
            </el-table-column>
            <el-table-column prop="it12sum" :label="t('common.score.sum')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.it12sum) }}
                </template>
            </el-table-column>
        </el-table-column>
        <el-table-column :label="t('common.level.e')">
            <el-table-column prop="et1st" :label="t('common.score.best')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.et1st) }}
                </template>
            </el-table-column>
            <el-table-column prop="et5th" :label="t('common.score.edge')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.et5th) }}
                </template>
            </el-table-column>
            <el-table-column prop="et5sum" :label="t('common.score.sum')" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.et5sum) }}
                </template>
            </el-table-column>
        </el-table-column>
        <el-table-column :label="t('common.level.sum')">
            <el-table-column :label="t('common.score.best')" sortable :sort-by="(r: GSCParticipant) => r.bt1st + r.it1st + r.et1st">
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.bt1st + row.it1st + row.et1st) }}
                </template>
            </el-table-column>
            <el-table-column :label="t('common.score.edge')" sortable, :sort-by="(r: GSCParticipant) => r.bt20th + r.it12th + r.et5th">
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.bt20th + row.it12th + row.et5th) }}
                </template>
            </el-table-column>
            <el-table-column :label="t('common.score.sum')" sortable :sort-by="(r: GSCParticipant) => r.bt20sum + r.it12sum + r.et5sum">
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.bt20sum + row.it12sum + row.et5sum) }}
                </template>
            </el-table-column>
        </el-table-column>
    </el-table>
</template>

<script setup lang="ts">

import { ElTable, ElTableColumn } from 'element-plus';
import { GSCParticipant } from '@/utils/gsc';
import PlayerName from '@/components/PlayerName.vue';
import { ms_to_s } from '@/utils';
import { useI18n } from 'vue-i18n';

defineProps({
    data: {
        type: Array<GSCParticipant>,
        default: () => [],
    },
});

const { t } = useI18n();

const emit = defineEmits(['row-click']);

function handleRowClick(row: GSCParticipant) {
    emit('row-click', row);
}

</script>
