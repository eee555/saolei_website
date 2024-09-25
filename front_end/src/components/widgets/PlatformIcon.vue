<template>
    <el-link :href="platformlist[platform].url" target="_blank" style="vertical-align: bottom;">
        {{ platformlist[platform].name }}
    </el-link>
</template>

<script setup lang="ts">
import { platformlist } from '@/utils/common/accountLinkPlatforms';

const data = defineProps({
    platform: {
        type: String,
        default: "",
    },
});
</script>