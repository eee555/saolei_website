<template>
    <el-link :href="`https://github.com/${props.username}`" underline="never" target="_blank">
        <el-image :src="`https://avatars.githubusercontent.com/${props.username}`" style="height: 26px; margin: 2px" />
        <span class="text">{{ props.username }}</span>
    </el-link>
</template>

<script setup lang="ts" name="GitHubUser">
import '@/styles/text.css';
import { ElImage, ElLink } from 'element-plus';

const props = defineProps({
    username: { type: String, required: true },
});

</script>
