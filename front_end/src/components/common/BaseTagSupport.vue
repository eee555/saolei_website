<template>
    <ElTag :type="support ? 'success' : 'danger'" size="small" effect="plain">
        <BaseIconTick v-if="support" />
        <BaseIconClose v-else />
        <slot />
    </ElTag>
</template>

<script setup lang="ts">
import { ElTag } from 'element-plus';

import { BaseIconClose, BaseIconTick } from '@/components/common/icon';

defineProps({
    support: {
        type: Boolean,
        default: true,
    },
});
</script>
