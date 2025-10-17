<template>
    <el-table-column
        prop="end_time" min-width="180" :formatter="simple_formatter(utc_to_local_format)"
        :sortable="sortable" :label="t('common.prop.end_time')"
    />
</template>

<script setup lang="ts">

import { ElTableColumn } from 'element-plus';
import { simple_formatter } from '@/utils';
import { utc_to_local_format } from '@/utils/system/tools';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

defineProps({
    sortable: { type: Boolean, default: false },
});

</script>
