<template>
    <el-link @click="visible = true">
        <slot />
    </el-link>
    <el-dialog v-model="visible" width="100%" align-center body-class="center" :show-close="false" @click="visible = false">
        <slot name="overlay" />
    </el-dialog>
</template>

<script lang="ts" setup>

import { ElDialog, ElLink } from 'element-plus';
import { ref } from 'vue';

const visible = ref(false);

</script>

<style scoped lang="less">
.el-dialog.center {
    display: flex;
    justify-content: center;
    align-items: center;
}
</style>
