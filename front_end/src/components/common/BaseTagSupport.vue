<template>
    <el-tag :type="support ? 'success' : 'danger'" size="small" effect="plain">
        <base-icon-tick v-if="support" />
        <base-icon-close v-else />
        <slot />
    </el-tag>
</template>

<script setup lang="ts">
import { ElTag } from 'element-plus';

import BaseIconClose from './BaseIconClose.vue';
import BaseIconTick from './BaseIconTick.vue';

defineProps({
    support: {
        type: Boolean,
        default: true,
    },
});

</script>
