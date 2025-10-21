<template>
    <!-- @vue-expect-error -->
    <el-link :href="platformlist[platform].url" target="_blank" style="vertical-align: bottom;">
        <!-- @vue-expect-error -->
        {{ platformlist[platform].name }}
    </el-link>
</template>

<script setup lang="ts">
import { ElLink } from 'element-plus';

import { platformlist } from '@/utils/common/accountLinkPlatforms';

defineProps({
    platform: {
        type: String,
        default: '',
    },
});
</script>
