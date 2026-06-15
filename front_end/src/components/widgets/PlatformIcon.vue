<template>
    <!-- @vue-expect-error -->
    <ElLink :href="platformlist[platform].url" target="_blank" rel="noopener noreferrer" style="vertical-align: bottom;">
        <!-- @vue-expect-error -->
        {{ platformlist[platform].name }}
    </ElLink>
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
