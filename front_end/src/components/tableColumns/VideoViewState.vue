<template>
    <el-table-column prop="state" width="40">
        <template #default="scope">
            <VideoStateIcon :state="scope.row.state" />
        </template>
    </el-table-column>
</template>

<script setup lang="ts">
import { ElTableColumn } from 'element-plus';

import VideoStateIcon from '../widgets/VideoStateIcon.vue';

</script>
