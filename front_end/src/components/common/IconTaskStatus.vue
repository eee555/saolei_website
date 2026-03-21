<template>
    <el-text v-if="status == 'loading'" type="primary">
        <i class="pi pi-spin pi-spinner-dotted" />
    </el-text>
    <el-text v-else-if="status == 'success'" type="success">
        <i class="pi pi-check-circle" />
    </el-text>
    <el-text v-else-if="status == 'error'" type="danger">
        <i class="pi pi-times-circle" />
    </el-text>
</template>

<script setup lang="ts">
import { ElText } from 'element-plus';
import { PropType } from 'vue';

import 'primeicons/primeicons.css';
import { TaskStatus } from '@/utils/common/structInterface';

defineProps({
    status: {
        type: String as PropType<TaskStatus>,
        default: '',
    },
});

</script>
