<template>
    <tippy interactive animate-fill arrow trigger="click" :append-to="'parent'">
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
import { ElLink } from 'element-plus';
import { Tippy } from 'vue-tippy';

import BaseCardNormal from '../common/BaseCardNormal.vue';
import BaseIconSetting from '../common/BaseIconSetting.vue';

</script>
