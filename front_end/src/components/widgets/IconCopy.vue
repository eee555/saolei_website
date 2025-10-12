<template>
    <el-link :underline="false" @click="copyToClipboard(text)">
        <base-icon-copy />
    </el-link>
</template>

<script setup lang="ts">

import BaseIconCopy from '@/components/common/BaseIconCopy.vue';
import { copyToClipboard } from './CopyToClipboard';
import { ElLink } from 'element-plus';

defineProps({
    text: {
        type: String,
        default: '',
    },
});

</script>
