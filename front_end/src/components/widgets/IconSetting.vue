<template>
    <tippy interactive animate-fill arrow trigger="click">
        <el-link :underline="false">
            <el-icon>
                <Setting />
            </el-icon>
        </el-link>
        <template #content>
            <el-card style="width: auto;">
                <slot />
            </el-card>
        </template>
    </tippy>
</template>

<script setup lang="ts">
import { Tippy } from 'vue-tippy';
import { ElLink, ElCard, ElIcon } from 'element-plus';
</script>

<style scoped lang="less">
.el-card {
    --el-card-padding: 10px;
}
</style>