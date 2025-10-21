<template>
    <el-table-column
        :label="t(`common.prop.${ stat}`)" align="right" :sortable="sortable"
        :sort-by="(row) => row.getStat(stat)"
    >
        <template #default="{row}: {row: VideoAbstract}">
            {{ row.displayStat(stat) }}
        </template>
    </el-table-column>
</template>

<script setup lang="ts">

import { ElTableColumn } from 'element-plus';
import { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import { getStat_stat, VideoAbstract } from '@/utils/videoabstract';

const { t } = useI18n();

defineProps({
    sortable: { type: Boolean, default: false },
    stat: { type: String as PropType<getStat_stat>, required: true },
});

</script>
