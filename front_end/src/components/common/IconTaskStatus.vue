<template>
    <span v-if="status == 'loading'" class="text text-primary">
        <i class="pi pi-spin pi-spinner-dotted" />
    </span>
    <span v-else-if="status == 'success'" class="text text-success">
        <i class="pi pi-check-circle" />
    </span>
    <span v-else-if="status == 'error'" class="text text-danger">
        <i class="pi pi-times-circle" />
    </span>
</template>

<script setup lang="ts">
import { PropType } from 'vue';

import '@/styles/text.css';
import 'primeicons/primeicons.css';
import { TaskStatus } from '@/utils/common/structInterface';

defineProps({
    status: {
        type: String as PropType<TaskStatus>,
        default: '',
    },
});

</script>
