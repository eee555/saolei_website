<template>
    {{ t('common.score.sum') }}{{ t('common.punct.colon') }}{{ T37 }}
    <el-table :data="data">
        <el-table-column>
            <template #default="scope">
                {{ indexMethod(scope.$index) }}
            </template>
        </el-table-column>
        <el-table-column prop="b" :label="t('common.level.b')" />
        <el-table-column prop="i" :label="t('common.level.i')" />
        <el-table-column prop="e" :label="t('common.level.e')" />
    </el-table>
</template>

<script setup lang="ts">
import { GSCParticipant } from '@/utils/gsc';
import { computed, PropType } from 'vue';
import { ElTable, ElTableColumn } from 'element-plus';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

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
        case 0: return t('common.score.best');
        case 1: return t('common.score.edge');
        case 2: return t('common.score.sum');
    }
}

</script>
