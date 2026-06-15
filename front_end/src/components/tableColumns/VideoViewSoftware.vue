<template>
    <ElTableColumn prop="software" width="40">
        <template #default="scope">
            <SoftwareIcon :state="scope.row.software" />
        </template>
    </ElTableColumn>
</template>

<script setup lang="ts">
import { ElTableColumn } from 'element-plus';

import SoftwareIcon from '../widgets/SoftwareIcon.vue';
</script>
