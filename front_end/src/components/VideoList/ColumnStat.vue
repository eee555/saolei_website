<template>
    <PrColumn :header="t(`common.prop.${ stat}`)" :sortable="sortable" :sort-field="(data) => data.getStat(stat)">
        <template #body="{data}: {data: VideoAbstract}">
            <el-text>{{ data.displayStat(stat) }}</el-text>
        </template>
    </PrColumn>
</template>

<script setup lang="ts">

import { ElText } from 'element-plus';
import PrColumn from 'primevue/column';
import { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import { getStat_stat, VideoAbstract } from '@/utils/videoabstract';

const { t } = useI18n();

defineProps({
    sortable: { type: Boolean, default: false },
    stat: { type: String as PropType<getStat_stat>, required: true },
});

</script>
