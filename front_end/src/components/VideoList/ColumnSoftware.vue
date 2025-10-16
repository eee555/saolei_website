<template>
    <el-table-column width="32">
        <template #default="{row}: {row: VideoAbstract}">
            <SoftwareIcon :software="row.software" style="margin: 0 -8px;" />
        </template>
    </el-table-column>
</template>

<script setup lang="ts">

import { ElTableColumn } from 'element-plus';
import SoftwareIcon from '@/components/widgets/SoftwareIcon.vue';
import { VideoAbstract } from '@/utils/videoabstract';

</script>
