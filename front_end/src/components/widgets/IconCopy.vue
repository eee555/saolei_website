<template>
    <ElLink underline="never" @click="copyToClipboard(text)">
        <BaseIconCopy />
    </ElLink>
</template>

<script setup lang="ts">
import { ElLink } from 'element-plus';

import { copyToClipboard } from './CopyToClipboard';

import { BaseIconCopy } from '@/components/common/icon';

defineProps({
    text: {
        type: String,
        default: '',
    },
});
</script>
