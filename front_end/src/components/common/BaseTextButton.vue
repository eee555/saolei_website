<template>
    <el-text :type="hovering ? 'primary' : undefined" :size="size" style="cursor: pointer;" @mouseenter="hovering = true" @mouseleave="hovering = false">
        <slot />
    </el-text>
</template>

<script setup lang="ts">

import { ElText } from 'element-plus';
import { PropType, ref } from 'vue';

defineProps({
    size: { type: String as PropType<'small' | 'default' | 'large'>, default: 'default' },
});

const hovering = ref(false);

</script>
