<template>
    <el-table-column
        :label="t(`common.prop.${ stat}`)" align="right" :sortable="sortable"
        :sort-by="(row) => row.getStat(stat)"
    >
        <template #default="scope">
            {{ scope.row.displayStat(stat) }}
        </template>
    </el-table-column>
</template>

<script setup lang="ts">

import { ElTableColumn } from 'element-plus';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

defineProps({
    sortable: { type: Boolean, default: false },
    stat: { type: String, required: true },
});

</script>
