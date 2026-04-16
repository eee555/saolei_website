<template>
    <span :class="['text', statusToClass[status]]">
        {{ status }}
    </span>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import { PropType } from 'vue';

import { DjangoTaskResultStatus } from '@/utils/common/structInterface';

const statusToClass = {
    'READY': 'text-primary',
    'RUNNING': 'text-warning',
    'SUCCESSFUL': 'text-success',
    'FAILED': 'text-danger',
    'NULL': 'text-info',
} as const;

defineProps({
    status: { type: String as PropType<DjangoTaskResultStatus>, default: 'NULL' },
});

</script>
