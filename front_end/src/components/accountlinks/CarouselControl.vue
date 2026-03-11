<template>
    <el-link :underline="false" :disabled="refCarousel?.activeIndex == 0" @click="refCarousel?.prev">
        <base-icon-prev />
    </el-link>
    <el-link :underline="false" :disabled="refCarousel?.activeIndex == length - 1" @click="refCarousel?.next">
        <base-icon-next />
    </el-link>
</template>

<script setup lang="ts">
import { ElCarousel, ElLink } from 'element-plus';
import { PropType } from 'vue';

import { BaseIconNext, BaseIconPrev } from '@/components/common/icon';

defineProps({
    refCarousel: {
        type: Object as PropType<typeof ElCarousel> | undefined,
        default: undefined,
    },
    length: {
        type: Number,
        required: true,
    },
});
</script>
