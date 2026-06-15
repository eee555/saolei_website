<template>
    <ElLink :href="`https://github.com/${props.username}`" underline="never" target="_blank" rel="noopener noreferrer">
        <ElImage :src="`https://avatars.githubusercontent.com/${props.username}`" style="height: 26px; margin: 2px" />
        <span class="text">{{ props.username }}</span>
    </ElLink>
</template>

<script setup lang="ts" name="GitHubUser">
import '@/styles/text.css';
import { ElImage, ElLink } from 'element-plus';

const props = defineProps({
    username: { type: String, required: true },
});
</script>
