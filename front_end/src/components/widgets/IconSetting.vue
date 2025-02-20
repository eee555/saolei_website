<template>
    <tippy interactive animate-fill arrow trigger="click">
        <el-link :underline="false">
            <base-icon-setting />
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
import { ElLink } from 'element-plus';
import BaseCardNormal from '../common/BaseCardNormal.vue';
import BaseIconSetting from '../common/BaseIconSetting.vue';
</script>
