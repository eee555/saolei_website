<template>
    <tippy interactive animate-fill arrow trigger="click">
        <el-link :underline="false">
            <el-icon>
                <Setting />
            </el-icon>
        </el-link>
        <template #content>
            <base-card-normal style="width: auto;">
                <slot />
            </base-card-normal>
        </template>
    </tippy>
</template>

<script setup lang="ts">
import { Tippy } from 'vue-tippy';
import { ElLink, ElIcon } from 'element-plus';
import BaseCardNormal from '../common/BaseCardNormal.vue';
</script>
