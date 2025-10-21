<template>
    <el-link :underline="false" @click="copyToClipboard(text)">
        <base-icon-copy />
    </el-link>
</template>

<script setup lang="ts">

import { ElLink } from 'element-plus';

import { copyToClipboard } from './CopyToClipboard';

import BaseIconCopy from '@/components/common/BaseIconCopy.vue';

defineProps({
    text: {
        type: String,
        default: '',
    },
});

</script>
