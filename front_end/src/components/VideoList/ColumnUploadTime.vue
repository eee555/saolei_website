<template>
    <el-table-column
        prop="upload_time" min-width="180" :formatter="simple_formatter(utc_to_local_format)"
        :sortable="sortable"
    />
</template>

<script setup lang="ts">

import { ElTableColumn } from 'element-plus';
import { simple_formatter } from '@/utils';
import { utc_to_local_format } from '@/utils/system/tools';

defineProps({
    sortable: { type: Boolean, default: false },
});

</script>
