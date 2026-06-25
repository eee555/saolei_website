<template>
    <ElLink v-if="length > 1" underline="never" :disabled="refCarousel?.activeIndex == 0" @click="refCarousel?.prev">
        <BaseIconPrev />
    </ElLink>
    <ElLink v-if="length > 1" underline="never" :disabled="refCarousel?.activeIndex == length - 1" @click="refCarousel?.next">
        <BaseIconNext />
    </ElLink>
</template>

<script setup lang="ts">
import type { ElCarousel } from 'element-plus';
import { ElLink } from 'element-plus';
import type { PropType } from 'vue';

import { BaseIconNext, BaseIconPrev } from '@/components/common/icon';

defineProps({
    refCarousel: {
        type: Object as PropType<typeof ElCarousel> | null,
        default: null,
    },
    length: {
        type: Number,
        required: true,
    },
});
</script>
