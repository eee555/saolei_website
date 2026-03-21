<template>
    <el-text :type="statusToType[status]">
        {{ status }}
    </el-text>
</template>

<script setup lang="ts">
import { ElText } from 'element-plus';
import { PropType } from 'vue';

import { DjangoTaskResultStatus } from '@/utils/common/structInterface';

const statusToType = {
    'READY': 'primary',
    'RUNNING': 'warning',
    'SUCCESSFUL': 'success',
    'FAILED': 'danger',
    'NULL': 'info',
} as const;

defineProps({
    status: { type: String as PropType<DjangoTaskResultStatus>, default: 'NULL' },
});

</script>
