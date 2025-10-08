<template>
    <el-table :data="data">
        <el-table-column prop="user__realname" sortable>
            <template #default="{ row }: { row: GSCParticipant }">
                <PlayerName :user-id="row.user__id" :user-name="row.user__realname" />
            </template>
        </el-table-column>
        <el-table-column label="初级">
            <el-table-column prop="bt1st" label="尖端" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.bt1st) }}
                </template>
            </el-table-column>
            <el-table-column prop="bt20th" label="边缘" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.bt20th) }}
                </template>
            </el-table-column>
            <el-table-column prop="bt20sum" label="总" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.bt20sum) }}
                </template>
            </el-table-column>
        </el-table-column>
        <el-table-column label="中级">
            <el-table-column prop="it1st" label="尖端" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.it1st) }}
                </template>
            </el-table-column>
            <el-table-column prop="it12th" label="边缘" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.it12th) }}
                </template>
            </el-table-column>
            <el-table-column prop="it12sum" label="总" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.it12sum) }}
                </template>
            </el-table-column>
        </el-table-column>
        <el-table-column label="高级">
            <el-table-column prop="et1st" label="尖端" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.et1st) }}
                </template>
            </el-table-column>
            <el-table-column prop="et5th" label="边缘" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.et5th) }}
                </template>
            </el-table-column>
            <el-table-column prop="et5sum" label="总" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.et5sum) }}
                </template>
            </el-table-column>
        </el-table-column>
        <el-table-column label="总计">
            <el-table-column label="尖端" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.bt1st + row.it1st + row.et1st) }}
                </template>
            </el-table-column>
            <el-table-column label="边缘" sortable>
                <template #default="{ row }: { row: GSCParticipant }">
                    {{ ms_to_s(row.bt20th + row.it12th + row.et5th) }}
                </template>
            </el-table-column>
            <el-table-column label="总" sortable>
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

defineProps({
    data: {
        type: Array<GSCParticipant>,
        default: () => [],
    },
});

</script>
