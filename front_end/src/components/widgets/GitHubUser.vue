<template>
    <el-link :href="`https://github.com/${props.username}`" :underline="false" target="_blank">
        <el-image :src="`https://avatars.githubusercontent.com/${props.username}`" style="height: 26px; margin: 2px" />
        <el-text>{{ props.username }}</el-text>
    </el-link>
</template>

<script setup lang="ts" name="GitHubUser">
import { ElLink, ElImage, ElText } from 'element-plus';
const props = defineProps({
    username: { type: String, required: true },
});

</script>
