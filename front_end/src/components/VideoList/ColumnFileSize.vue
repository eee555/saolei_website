<template>
    <el-table-column :label="t('common.prop.file_size')" align="right" prop="file_size" :sortable="sortable">
        <template #default="{row}: {row: VideoAbstract}">
            {{ row.file_size === 0 ? '-' : formatBytes(row.file_size) }}
        </template>
    </el-table-column>
</template>

<script setup lang="ts">

import { ElTableColumn } from 'element-plus';
import { formatBytes } from '@/utils/strings';
import { useI18n } from 'vue-i18n';
import { VideoAbstract } from '@/utils/videoabstract';

const { t } = useI18n();

defineProps({
    sortable: { type: Boolean, default: false },
});

</script>
