<template>
    <el-table-column label="文件大小" align="right" prop="file_size" :sortable="sortable">
        <template #default="scope">
            {{ scope.row.file_size === 0 ? '-' : formatBytes(scope.row.file_size) }}
        </template>
    </el-table-column>
</template>

<script setup lang="ts">

import { ElTableColumn } from 'element-plus';
import { formatBytes } from '@/utils/strings';

defineProps({
    sortable: { type: Boolean, default: false },
});

</script>
