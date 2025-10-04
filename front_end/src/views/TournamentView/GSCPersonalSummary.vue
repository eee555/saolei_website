<template>
    总成绩：{{ T37 }}
    <el-table :data="data">
        <el-table-column>
            <template #default="scope">
                {{ indexMethod(scope.$index) }}
            </template>
        </el-table-column>
        <el-table-column prop="b" label="初级" />
        <el-table-column prop="i" label="中级" />
        <el-table-column prop="e" label="高级" />
    </el-table>
</template>

<script setup lang="ts">
import { GSCParticipant } from '@/utils/gsc';
import { computed, PropType } from 'vue';
import { ElTable, ElTableColumn } from 'element-plus';

const props = defineProps({
    participant: {
        type: Object as PropType<GSCParticipant>,
        required: true,
    },
});

const data = computed(() => {
    return [
        { 'b': props.participant.bt1st, 'i': props.participant.it1st, 'e': props.participant.et1st },
        { 'b': props.participant.bt20th, 'i': props.participant.it12th, 'e': props.participant.et5th },
        { 'b': props.participant.bt20sum, 'i': props.participant.it12sum, 'e': props.participant.et5sum },
    ];
});

const T37 = computed(() => {
    return props.participant.bt20sum + props.participant.it12sum + props.participant.et5sum;
});

function indexMethod(index: number) {
    switch (index) {
        case 0: return '尖端成绩';
        case 1: return '边缘成绩';
        case 2: return '总成绩';
    }
}

</script>
