<template>
    <el-table-column prop="software" width="40">
        <template #default="scope">
            <SoftwareIcon :state="scope.row.software" />
        </template>
    </el-table-column>
</template>

<script setup lang="ts">

import SoftwareIcon from '../widgets/SoftwareIcon.vue';

</script>